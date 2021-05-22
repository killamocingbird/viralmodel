import distributions
import math
import numpy as np
import os
import projections
import random
import sys


# Interface for models
class Model_Backbone:
    def __init__(self, cfg, pfs):
        self.cfg = cfg
        self.pfs = pfs
        self.data = dict()

    # ToImplement
    def forward(self):
        pass
    
    # Dumps the data into a file
    def dump(self, file_name):
        np.save(os.path.join(self.cfg.PATHS.DUMP_PATH, file_name), self.data)
    

class Base(Model_Backbone):
    def __init__(self, cfg, pfs):
        super().__init__(cfg, pfs)
        
        self.infected = set()
        self.recovered = set()
        
        self.generate_pop()
        self.generate_locations()
    
        self.proj = None
        self.log_deltas = False
        self.deltas = None
    
    
    def assign_proj(self, proj, log_deltas=True):
        assert isinstance(proj, projections.Projection_Backbone)
        self.proj = proj
        self.log_deltas = log_deltas
        self.deltas = np.zeros((0, len(proj.groups), len(proj.groups)))
    
    
    def generate_pop(self):
        # [id, Age, SIR (0, 1, 2), Days since infection] 
        self.data['POP'] = np.zeros((self.cfg.RUN.POP, 4), dtype=np.long)
        dat = self.data['POP']
        dat[:,0] = np.arange(len(self.data['POP']))
        
        # Generate ages according to distribution if provided else uniform
        if self.cfg.RUN.POP_DIST is None:
            dat[:,1] = np.random.randint(self.pfs.POP.MIN_AGE,
                                         self.pfs.POP.MAX_AGE + 1,
                                         len(dat))
        else:
            dist_file = self.cfg.RUN.POP_DIST
            assert os.path.isfile(dist_file), "Distribution file invalid"
            pmf = np.load(dist_file, allow_pickle=True)
            dat[:,1] = distributions.sample(self.pfs.POP.MIN_AGE,
                                            self.pfs.POP.MAX_AGE,
                                            pmf, num_samples=len(dat))
            
        SIR_array = np.zeros((self.cfg.RUN.POP))
        DSI_array = np.zeros((self.cfg.RUN.POP))
        num_I = int(self.cfg.RUN.INIT_I * self.cfg.RUN.POP)
        num_R = int(self.cfg.RUN.INIT_R * self.cfg.RUN.POP)
        SIR_array[:num_I] = 1
        # Randomly sample DSI
        DSI_array[:num_I] = np.random.randint(0, self.pfs.DN.RT, num_I)
        SIR_array[num_I:num_I + num_R] = 2
        perm = np.random.permutation(self.cfg.RUN.POP)
        dat[:,2] = SIR_array[perm]
        dat[:,3] = DSI_array[perm]
        
        # Create entrees in structured pop dataset
        self.data['POP_struct'] = [{'id': dat[i,0],
                                    'age': dat[i,1],
                                    'SIR': dat[i,2],
                                    'DSI': dat[i,3],
                                    } for i in range(len(dat))]
        
        
        # Fill infected set
        self.infected.update(dat[dat[:,2] == 1, 0])
        # Fill recovered set
        self.recovered.update(dat[dat[:,2] == 2, 0])
        
    
    def generate_locations(self):
        assert 'POP' in self.data
        
        keys = list(set(self.pfs.keys()).difference(set(['DN', 'POP'])))
        # Keys: HH, SC, WK, SH
        
        for i in range(len(keys)):
            key = keys[i]
            self.data[key] = []
            dat = self.data[key]
            # Grab all eligible people
            ppl = self.data['POP'][((self.pfs[key].MIN_AGE <= self.data['POP'][:,1]) * 
                                    (self.data['POP'][:,1] <= self.pfs[key].MAX_AGE))]
            # Permutation for random selection
            perm = np.random.permutation(len(ppl))
            added = 0
            idx = 0
            
            while added < len(ppl):
                # Generate location and assign people
                dat.append(
                    {'id': idx,
                     'POP': ppl[perm[added:added + random.randint(self.pfs[key].MIN_POP,
                                                                  self.pfs[key].MAX_POP)]]}
                )
                
                # Assign location to people
                for pop in dat[-1]['POP']:
                    self.data['POP_struct'][pop[0]][key] = idx
                
                added += len(dat[-1]['POP'])
                idx += 1
    
    """
    In this model, each forward step represents a day. All people are assigned a household
    and begin their day with 8 hours in their household. Then they are sent to work for 8
    hours or their primary occupation. Finally, they return home and those with a secondary
    gathering location will go there for approximately one hour. Then finally everyone returns
    home for 16 hours.
    """
    def forward(self):
        # Clean out temporary deltas matrix for logging
        if self.log_deltas:
            self.clean_deltas()
        
        # Simulate 8 hours at home
        self.simulate('HH', 8)            
        
        # Simulate primary occupation
        self.simulate('WK', 8)
        self.simulate('SC', 8)        
        
        # Simulate secondary
        self.simulate('SH', 1)
        
        # Simulate the rest of the night
        self.simulate('HH', 16)
        
        # Increment DSI and simulate recovery
        self.recovery()
        
        # Aggregate deltas into record
        if self.log_deltas:
            self.agg_deltas()
        
        # Return new SIR
        return self.SIR()
    
    
    def clean_deltas(self):
        assert self.log_deltas, "Delta logging is not enabled."
        assert self.proj, "No projectile scheme to log deltas."
        
        # Create empty 2D
        self.deltas_temp = np.zeros((len(self.proj.groups), len(self.proj.groups)))
        
    
    def agg_deltas(self):
        self.deltas = np.concatenate((self.deltas, self.deltas_temp[None,:,:]), 0)
        
    
    def dump_deltas(self, file_name, include_past=False):
        ret = self.deltas if include_past else self.deltas[-1]
        np.save(os.path.join(self.cfg.PATHS.DUMP_PATH, file_name), ret)
    
    # Simulates time hours in the specified location key
    def simulate(self, key, time):
        assert key in self.data, "Key %s does not exist." % key
        
        for loc in self.data[key]:
            infected = list(self.infected.intersection(loc['POP'][:,0]))
            susceptible = list(set(loc['POP'][:,0]).difference(infected).difference(self.recovered))
            if len(susceptible) != 0 and len(infected) != 0:
                # Generate list of interactions
                interactions = np.random.randint(0, len(loc['POP'][:,0])-1, math.ceil(time * self.pfs[key].IPH) * len(infected))
                
                if self.log_deltas:
                    # Get groups of infected and susceptible
                    inf_groups = self.proj.get_group(infected)
                    sus_groups = self.proj.get_group(susceptible)
                    # Group interactions
                    gr_interactions = interactions.reshape((len(infected), -1))
                    gr_inter = [np.unique(gr_interactions[i][gr_interactions[i] < len(susceptible)], return_counts=True) 
                                for i in range(len(gr_interactions))]
                    for i in range(len(gr_inter)):
                        for j in range(len(gr_inter[i][0])):
                            # Avoid double counting infections
                            if self.data['POP'][susceptible[gr_inter[i][0][j]],2] == 1:
                                continue
                            if (np.random.rand(gr_inter[i][1][j]) < self.pfs.DN.IPI).any():
                                self.data['POP'][susceptible[gr_inter[i][0][j]],2] = 1
                                self.data['POP_struct'][susceptible[gr_inter[i][0][j]]]['SIR'] = 1
                                self.infected.add(susceptible[gr_inter[i][0][j]])
                                # Add to deltas matrix
                                self.deltas_temp[inf_groups[i], sus_groups[gr_inter[i][0][j]]] += 1
                    
                else:
                    # Filter out interactions with only those susceptible
                    interactions = interactions[interactions < len(susceptible)]
                    
                    inter, freq = np.unique(interactions, return_counts=True)
                    for i in range(len(inter)):
                        if (np.random.rand(freq[i]) < self.pfs.DN.IPI).any():
                            self.data['POP'][susceptible[inter[i]],2] = 1
                            self.data['POP_struct'][susceptible[inter[i]]]['SIR'] = 1
                            self.infected.add(susceptible[inter[i]])
        
    # Counts up DSI for each infected agent and simulates recovery if above threshold
    def recovery(self):
        recovered = set()
        for idx in self.infected:
            self.data['POP'][idx,3] += 1
            self.data['POP_struct'][idx]['DSI'] += 1
            # Recovery if DSI is above RT
            if self.data['POP'][idx,3] >= self.pfs.DN.RT:
                self.data['POP'][idx,2] = 2
                self.data['POP_struct'][idx]['SIR'] = 2
                recovered.add(idx)
        # Remove from infected pool
        self.infected = self.infected.difference(recovered)
        # Add into recovered pool
        self.recovered.update(recovered)
            
        
    def SIR(self):
        return np.array([len(self.data['POP']) - len(self.infected) - len(self.recovered), len(self.infected), len(self.recovered)])
            
            
# Helper function to get classes from string
def get_model(classname):
    return getattr(sys.modules[__name__], classname)
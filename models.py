import math
import numpy as np
import random
import sys

class Base:
    
    def __init__(self, cfg, pfs):
        self.cfg = cfg
        self.pfs = pfs
        
        self.data = dict()
        self.infected = set()
        self.recovered = set()
        
        self.generate_pop()
        self.generate_locations()
    
    
    def generate_pop(self):
        # [id, Age, SIR (0, 1, 2), Days since infection] 
        self.data['POP'] = np.zeros((self.cfg.RUN.POP, 4), dtype=np.long)
        dat = self.data['POP']
        dat[:,0] = np.arange(len(self.data['POP']))
        dat[:,1] = np.random.randint(self.pfs.POP.MIN_AGE,
                                     self.pfs.POP.MAX_AGE + 1,
                                     len(dat))
        SIR_array = np.zeros((self.cfg.RUN.POP))
        num_I = int(self.cfg.RUN.INIT_I * self.cfg.RUN.POP)
        num_R = int(self.cfg.RUN.INIT_R * self.cfg.RUN.POP)
        SIR_array[:num_I] = 1
        SIR_array[num_I:num_I + num_R] = 2
        dat[:,2] = SIR_array[np.random.permutation(self.cfg.RUN.POP)]
        
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
        
        # Return new SIR
        return self.SIR()
    
    
    # Simulates time hours in the specified location key
    def simulate(self, key, time):
        assert key in self.data, "Key %s does not exist." % key
        
        for loc in self.data[key]:
            infected = list(self.infected.intersection(loc['POP'][:,0]))
            susceptible = list(set(loc['POP'][:,0]).difference(infected).difference(self.recovered))
            if len(susceptible) != 0:
                # Generate list of interactions
                interactions = np.random.randint(0, len(loc['POP'][:,0])-1, math.ceil(time * self.pfs[key].IPH * len(infected)))
                # Filter out interactions with only those susceptible
                interactions = interactions[interactions < len(susceptible)]
                
                inter, freq = np.unique(interactions, return_counts=True)
                for i in range(len(inter)):
                    if (np.random.rand(freq[i]) < self.pfs.DN.IPI).any():
                        self.data['POP'][inter[i],2] = 1
                        self.data['POP_struct'][inter[i]]['SIR'] = 1
                        self.infected.add(inter[i])
        
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
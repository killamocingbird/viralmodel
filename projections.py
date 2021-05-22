import models
import numpy as np
import os
import sys


class Projection_Backbone:
    def __init__(self, model):
        assert isinstance(model, models.Model_Backbone)
        self.model = model
        
    # Perform projection
    def project(self):
        pass
    
     # Gets the group index given an agent index; should be able to be tenorized
    def get_group(self, agent_idx):
        pass
    
    def dump(self, file_name):
        np.save(os.path.join(self.model.cfg.PATHS.DUMP_PATH, file_name), self.project())


class Age(Projection_Backbone):
    def __init__(self, model):
        super().__init__(model)
        self.groups = [
            [1, 4],
            [5, 18],
            [19, 65],
            [66, 80]
        ]
        self.group_separations = np.array([4, 18, 65])
        
    # Perform projection
    def project(self):
        ret = np.zeros((len(self.groups), 3))
        dat = self.model.data['POP']
        for i in range(len(self.groups)):
            group = self.groups[i]
            g_dat = dat[(group[0] <= dat[:,1]) * (dat[:,1] <= group[1])]
            sir, freq = np.unique(g_dat[:,2], return_counts=True)
            ret[i,sir] = freq
        return ret
    
    # Gets the group index given an agent index. Can be tensorized
    def get_group(self, agent_idx):
        ages = self.model.data['POP'][agent_idx][:,1]
        return np.searchsorted(self.group_separations, ages)
        
    
# Helper function to get classes from string
def get_projection(classname):
    return getattr(sys.modules[__name__], classname)



import matplotlib.pyplot as plt
import models
import numpy as np
import os
import projections

def check_cfg(cfg):
    # Check for profile configuration
    assert os.path.isfile(cfg.PATHS.PROFILES_PATH), "Must include a profile yaml."
    
    # Check model exists
    try:
        models.get_model(cfg.RUN.MODEL)
    except AttributeError:
        assert False, "Model %s does not exist." % cfg.RUN.MODEL
        
    # Check SIR distribution
    total = cfg.RUN.INIT_S + cfg.RUN.INIT_I + cfg.RUN.INIT_R
    assert abs(total - 1) < 1e-7, "SIR distribution must be a probability."
    
    
def get_model(cfg, pfs):
    return models.get_model(cfg.RUN.MODEL)(cfg, pfs)

def get_projection(cfg, model):
    return projections.get_projection(cfg.RUN.PROJECTION)(model)


def plot_SIR(SIR):
    fig = plt.figure()
    xax = [i for i in range(1, len(SIR) + 1)]
    plt.plot(xax, SIR[:,0], xax, SIR[:,1], xax, SIR[:,2])
    plt.legend(['Susceptible', 'Infected', 'Recovered'])
    plt.grid()
    plt.xlabel('Time (Days)')
    plt.ylabel('Number')
    plt.xlim([1, len(SIR)])

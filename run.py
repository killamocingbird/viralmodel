from base_profile import pfs
from config import cfg

import click
import numpy as np
from tqdm import tqdm
import util


#@click.command()
#@click.argument('config_file')
def run(config_file):
    # Load in config and check values
    cfg.merge_from_file(config_file)
    cfg.freeze()
    util.check_cfg(cfg)
    
    # Load in profile
    pfs.merge_from_file(cfg.PATHS.PROFILES_PATH)
    pfs.freeze()
    
    # Load in model
    model = util.get_model(cfg, pfs)
    # return model
    
    SIR = np.zeros((0, 3))
    for iteration in tqdm(range(cfg.RUN.ITERS)):
        SIR = np.concatenate((SIR, model.forward()[None,:]), 0)
        
    return SIR


if __name__ == '__main__':
    #model = run('scenarios/base/config.yaml')
    SIR = run('scenarios/base/config.yaml')
    util.plot_SIR(SIR)

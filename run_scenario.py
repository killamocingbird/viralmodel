from base_profile import pfs
from config import cfg

import numpy as np
import os
from tqdm import tqdm
import util


def run(config_file, verbose=False):
    # Load in config and check values
    cfg.merge_from_file(config_file)
    cfg.freeze()
    util.check_cfg(cfg)
    
    # Load in profile
    pfs.merge_from_file(cfg.PATHS.PROFILES_PATH)
    pfs.freeze()
    
    # Load in model
    model = util.get_model(cfg, pfs)
    # Load in projection
    proj = util.get_projection(cfg, model)
    
    # Set up file dumping / logging
    dump_path = cfg.PATHS.DUMP_PATH
    if not os.path.exists(dump_path):
        os.makedirs(dump_path)
    
    SIR = model.SIR()[None, :]
    # Initial dump
    model.dump('raw_init')
    proj.dump('proj_init')
    for iteration in tqdm(range(cfg.RUN.ITERS)) if verbose else range(cfg.RUN.ITERS):
        SIR = np.concatenate((SIR, model.forward()[None,:]), 0)
        model.dump('raw_%d' % iteration)
        proj.dump('proj_%d' % iteration)
        
    return SIR


if __name__ == '__main__':
    SIR = run('scenarios/base/config.yaml')
    util.plot_SIR(SIR)

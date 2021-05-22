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
    # Register projection into model and enable delta logging
    model.assign_proj(proj, log_deltas=True)
    
    # Set up file dumping / logging
    dump_path = cfg.PATHS.DUMP_PATH
    if not os.path.exists(dump_path):
        os.makedirs(dump_path)
    
    SIR = model.SIR()[None, :]
    # Initial dump
    proj.dump('proj__0')
    for iteration in tqdm(range(cfg.RUN.ITERS)) if verbose else range(cfg.RUN.ITERS):
        SIR = np.concatenate((SIR, model.forward()[None,:]), 0)
        proj.dump('proj_%d' % iteration)
        model.dump_deltas('deltas_%d' % iteration)
        
    return SIR


if __name__ == '__main__':
    config_path = 'scenarios/test'
    config_file = 'config.yaml'
    os.chdir(config_path)
    SIR = run(config_file)
    util.plot_SIR(SIR)

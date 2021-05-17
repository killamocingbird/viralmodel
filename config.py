"""
Default configuration file for a simulation run runs
"""

from yacs.config import CfgNode as CN

_C = CN()

### System variables ###
_C.SYSTEM = CN()
_C.SYSTEM.SEED = 1
# Label for run, if duplicate will override previous data
_C.SYSTEM.HEADER = ''
# Whether or not to print to cout as well as dump to file
_C.SYSTEM.DEBUG = True


### Path variables ###
_C.PATHS = CN()
_C.PATHS.PROFILES_PATH = ''
_C.PATHS.DUMP_PATH = '../out/' + _C.SYSTEM.HEADER


### Simulation variables ###
_C.RUN = CN()
# Simulation Model
_C.RUN.MODEL = ''
# Simulation iteration (1 day per iteration)
_C.RUN.ITERS = 90
# Population
_C.RUN.POP = 100000
# Percentage SIR to start with
_C.RUN.INIT_S = 0.999
_C.RUN.INIT_I = 0.001
_C.RUN.INIT_R = 0

cfg = _C
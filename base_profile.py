"""
Default configuration file for a simulation profile
"""

from yacs.config import CfgNode as CN

_C = CN()

"""
Acryonyms
DN: Disease
HH: Household
SC: School
WK: Work
SH: Shopping Center / Store

IPI: Infections per Interaction
IPH: Interactions per hour
RT: Recovery time
"""

### Disease Information ###
_C.DN = CN()
_C.DN.IPI = 0.05
_C.DN.RT = 5

### Population Information ###
_C.POP = CN()
_C.POP.MIN_AGE = 1
_C.POP.MAX_AGE = 80

### Household Information ###
_C.HH = CN()
# Minimum and maximum values will be uniformly sampled
_C.HH.MIN_POP = 1
_C.HH.MAX_POP = 7
_C.HH.MIN_AGE = _C.POP.MIN_AGE
_C.HH.MAX_AGE = _C.POP.MAX_AGE
_C.HH.IPH = 0.5


### School Information ###
_C.SC = CN()
_C.SC.MIN_POP = 1000
_C.SC.MAX_POP = 5000
_C.SC.MIN_AGE = 5
_C.SC.MAX_AGE = 18
_C.SC.IPH = 1


### Work Information ###
_C.WK = CN()
_C.WK.MIN_POP = 50
_C.WK.MAX_POP = 2000
_C.WK.MIN_AGE = 19
_C.WK.MAX_AGE = 65
_C.WK.IPH = 0.2


### Shopping Store Information ###
_C.SH = CN()
_C.SH.MIN_POP = 2000
_C.SH.MAX_POP = 10000
_C.SH.MIN_AGE = 20
_C.SH.MAX_AGE = 80
_C.SH.IPH = 0.8


pfs = _C
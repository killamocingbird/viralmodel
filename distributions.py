import numpy as np
from scipy.stats import norm

# Obtains sum of normal distributions given centers and spreads and returns PMF
def normal_sum_pmf(min_val, max_val, centers, spreads):
    assert len(centers) == len(spreads)
    ret = np.zeros((max_val - min_val + 1))
    for i in range(len(centers)):
        ret += norm.pdf([i for i in range(min_val, max_val + 1)], centers[i], spreads[i])
        
    # Normalize into PDF
    ret /= ret.sum()
    
    return ret


# Draws discrete samples from given discrete PMF
def sample(min_val, max_val, pmf, num_samples=1):
    assert (max_val - min_val + 1) == len(pmf), "PMF must be one-to-one with range"
    cmf = np.cumsum(pmf)
    
    # Inverse transform sampling of uniform to sample from pmf
    return cmf.searchsorted(np.random.rand(num_samples))
    

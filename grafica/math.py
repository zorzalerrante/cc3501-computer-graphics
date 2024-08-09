import numpy as np
#from numba import jit

#@jit
def normalize(x):
    x /= np.linalg.norm(x)
    return x
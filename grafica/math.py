import numpy as np

def normalize(x):
    x /= np.linalg.norm(x)
    return x
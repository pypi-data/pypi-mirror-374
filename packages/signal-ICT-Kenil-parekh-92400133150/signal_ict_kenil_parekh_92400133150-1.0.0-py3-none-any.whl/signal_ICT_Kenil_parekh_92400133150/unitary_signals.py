import numpy as np

def unit_step(n):
    return np.array([1 if i >= 0 else 0 for i in n])

def unit_impulse(n):
    return np.array([1 if i == 0 else 0 for i in n])

def ramp_signal(n):
    return np.array([i if i >= 0 else 0 for i in n])


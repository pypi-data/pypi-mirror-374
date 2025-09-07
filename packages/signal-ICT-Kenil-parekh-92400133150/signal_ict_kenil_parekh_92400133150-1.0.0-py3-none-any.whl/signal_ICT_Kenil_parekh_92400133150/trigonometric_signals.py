import numpy as np

def sine_wave(A, f, phi, t):
    return A * np.sin(2 * np.pi * f * t + phi)

def cosine_wave(A, f, phi, t):
    return A * np.cos(2 * np.pi * f * t + phi)

def exponential_signal(A, a, t):
    return A * np.exp(a * t)


import numpy as np

def time_shift(signal, n, k):
    return n + k, signal

def time_scale(signal, n, k):
    return n * k, signal

def signal_addition(sig1, sig2, n):
    return sig1 + sig2

def signal_multiplication(sig1, sig2, n):
    return sig1 * sig2


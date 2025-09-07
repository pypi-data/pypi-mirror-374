import numpy as np

'''Unit Step signal u(n) = 1 for n>=0 else 0'''
def unit_step(n):
    a = np.where(n >= 0, 1, 0)
    return a

'''Unit Impulse signal delta(n) = 1 for n=0 else 0'''
def unit_impulse(n):
    b = np.where(n == 0, 1, 0)
    return b

'''Ramp signal r(n) = n for n>=0 else 0'''
def ramp_signal(n):
    c = np.where(n >= 0, n, 0)
    return c

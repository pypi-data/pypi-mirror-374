# trig_signals.py
import numpy as np

'''Generate a sine wave: A*sin(2*pi*f*t + phi)'''
def sine_wave(A, f, phi, t):
    x = A * np.sin(2 * np.pi * f * t + phi)
    return x

'''Generate a cosine wave: A*cos(2*pi*f*t + phi)'''
def cosine_wave(A, f, phi, t):
    y = A * np.cos(2 * np.pi * f * t + phi)
    return y

'''Generate an exponential signal: A*e^(a*t)'''
def exponential_signal(A, a, t):
    z = A * np.exp(a * t)
    return z

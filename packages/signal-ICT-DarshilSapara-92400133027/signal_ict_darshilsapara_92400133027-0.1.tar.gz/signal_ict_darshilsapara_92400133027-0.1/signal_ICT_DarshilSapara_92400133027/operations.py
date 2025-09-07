import numpy as np

# -----------------------
# 1. Time Shift
# -----------------------
def time_shift(signal, k):
    shifted_signal = np.roll(signal, k)
    if k > 0:
        shifted_signal[:k] = 0  # zero padding for right shift
    elif k < 0:
        shifted_signal[k:] = 0  # zero padding for left shift
    return shifted_signal

# -----------------------
# 2. Time Scale
# -----------------------
def time_scale(signal, k):
    n = np.arange(len(signal))
    scaled_n = np.arange(0, len(signal), k)
    scaled_signal = np.interp(scaled_n, n, signal)  # linear interpolation
    return scaled_signal

# -----------------------
# 3. Signal Addition
# -----------------------
def signal_addition(signal1, signal2):
    max_len = max(len(signal1), len(signal2))
    s1 = np.pad(signal1, (0, max_len - len(signal1)), 'constant')
    s2 = np.pad(signal2, (0, max_len - len(signal2)), 'constant')
    return s1 + s2

# -----------------------
# 4. Signal Multiplication
# -----------------------
def signal_multiplication(signal1, signal2):
    max_len = max(len(signal1), len(signal2))
    s1 = np.pad(signal1, (0, max_len - len(signal1)), 'constant')
    s2 = np.pad(signal2, (0, max_len - len(signal2)), 'constant')
    return s1 * s2

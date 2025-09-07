"""
Simple signal operations: time shift, time scale (integer), addition, multiplication.
"""
import numpy as np

def time_shift(signal, k):
    """
    Shift signal by k samples.
    Positive k => shift right (delay) and pad with zeros on the left.
    Negative k => shift left (advance) and pad zeros on the right.
    """
    sig = np.array(signal)
    L = len(sig)
    if k == 0:
        return sig.copy()
    if k > 0:
        if k >= L:
            return np.zeros_like(sig)
        return np.concatenate((np.zeros(k), sig[:L - k]))
    else: # k < 0 -> left shift
        k_abs = abs(k)
        if k_abs >= L:
            return np.zeros_like(sig)
        return np.concatenate((sig[k_abs:], np.zeros(k_abs)))

def time_scale(signal, k):
    """
    Integer time scaling (downsampling by integer factor).
    k : integer > 0
    Example: k=2 returns every 2nd sample.
    (This is a simple approach; it does not add interpolation.)
    """
    if k <= 0 or not isinstance(k, int):
        raise ValueError("k must be a positive integer for simple time_scale.")
    sig = np.array(signal)
    return sig[::k]

def signal_addition(signal1, signal2):
    """
    Add two signals aligning from start; result length = min(len1,len2)
    """
    s1 = np.array(signal1)
    s2 = np.array(signal2)
    n = min(len(s1), len(s2))
    return s1[:n] + s2[:n]

def signal_multiplication(signal1, signal2):
    """
    Point-wise multiplication; result length = min(len1,len2)
    """
    s1 = np.array(signal1)
    s2 = np.array(signal2)
    n = min(len(s1), len(s2))
    return s1[:n] * s2[:n]

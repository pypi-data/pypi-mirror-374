"""
Trigonometric and exponential signals.
Each function returns a NumPy array and plots the signal.
"""
import numpy as np
import matplotlib.pyplot as plt

def sine_wave(A, f, phi, t):
    """
    A : amplitude
    f : frequency in Hz
    phi: phase in radians
    t : time vector (numpy array)
    """
    t = np.array(t)
    signal = A * np.sin(2 * np.pi * f * t + phi)
    plt.plot(t, signal)
    plt.title(f"Sine Wave: A={A}, f={f} Hz")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def cosine_wave(A, f, phi, t):
    t = np.array(t)
    signal = A * np.cos(2 * np.pi * f * t + phi)
    plt.plot(t, signal)
    plt.title(f"Cosine Wave: A={A}, f={f} Hz")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def exponential_signal(A, a, t):
    """
    A : amplitude (initial)
    a : exponent coefficient (e.g., -1 for decay)
    t : time vector
    """
    t = np.array(t)
    signal = A * np.exp(a * t)
    plt.plot(t, signal)
    plt.title(f"Exponential Signal: A={A}, a={a}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

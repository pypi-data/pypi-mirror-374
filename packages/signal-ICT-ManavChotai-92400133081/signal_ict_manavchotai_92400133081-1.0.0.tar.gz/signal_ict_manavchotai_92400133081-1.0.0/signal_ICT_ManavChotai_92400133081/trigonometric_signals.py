# trig_signals.py
import numpy as np

# Sine Wave
def sine_wave(A, f, phi, t):
    return A * np.sin(2 * np.pi * f * t + phi)

# Cosine Wave
def cosine_wave(A, f, phi, t):
    return A * np.cos(2 * np.pi * f * t + phi)

# Exponential Signal
def exponential_signal(A, a, t):
    return A * np.exp(a * t)

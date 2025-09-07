# unitary_signals.py
import numpy as np

# Unit Step Signal
def unit_step(n):
    return np.where(n >= 0, 1, 0)

# Unit Impulse Signal
def unit_impulse(n):
    return np.where(n == 0, 1, 0)

# Ramp Signal
def ramp_signal(n):
    return np.where(n >= 0, n, 0)

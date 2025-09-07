# operations.py
import numpy as np

# -----------------------------
# 1. Time shift for continuous signals
# -----------------------------
def time_shift_continuous(signal_func, t, shift, *args):
    """
    Shift a continuous-time signal by 'shift' units.
    signal_func: function of the signal (like sine_wave)
    t: time array
    shift: amount to shift (+ for right, - for left)
    *args: parameters for the signal function
    """
    return signal_func(*args, t - shift)

# -----------------------------
# 2. Signal addition (discrete signals)
# -----------------------------
def signal_addition(x1, x2, n):
    """
    Add two discrete-time signals of same length
    """
    return np.array(x1) + np.array(x2)

# -----------------------------
# 3. Signal multiplication (continuous or discrete)
# -----------------------------
def signal_multiplication(x1, x2, t=None):
    """
    Multiply two signals (x1 and x2 must have same length)
    """
    return np.array(x1) * np.array(x2)

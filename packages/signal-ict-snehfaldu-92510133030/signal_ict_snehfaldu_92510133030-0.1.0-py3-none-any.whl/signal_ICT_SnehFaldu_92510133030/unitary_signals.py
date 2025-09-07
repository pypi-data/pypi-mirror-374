"""
Unitary signals: unit step, unit impulse, ramp.
Each function returns a NumPy array and plots the signal.
"""
import numpy as np
import matplotlib.pyplot as plt

def unit_step(n):
    """
    n : array-like of sample indices (e.g., np.arange(0,20))
    returns: numpy array of 0/1
    """
    n = np.array(n)
    signal = np.where(n >= 0, 1, 0).astype(float)
    plt.stem(n, signal)
    plt.title("Unit Step Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def unit_impulse(n):
    """
    n : array-like of sample indices
    returns: numpy array with 1 at n==0 else 0
    """
    n = np.array(n)
    signal = np.where(n == 0, 1.0, 0.0)
    plt.stem(n, signal)
    plt.title("Unit Impulse (Delta) Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def ramp_signal(n):
    """
    n : array-like of sample indices
    returns: numpy array with ramp (n for n>=0, else 0)
    """
    n = np.array(n)
    signal = np.where(n >= 0, n.astype(float), 0.0)
    plt.stem(n, signal)
    plt.title("Ramp Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

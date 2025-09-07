import numpy as np
import matplotlib.pyplot as plt

def unit_step(n):
    signal = np.where(n >= 0, 1, 0)
    plt.figure()
    plt.stem(n, signal)
    plt.title("Unit Step Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def unit_impulse(n):
    signal = np.where(n == 0, 1, 0)
    plt.figure()
    plt.stem(n, signal)
    plt.title("Unit Impulse Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def ramp_signal(n):
    signal = np.where(n >= 0, n, 0)
    plt.figure()
    plt.stem(n, signal)
    plt.title("Ramp Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

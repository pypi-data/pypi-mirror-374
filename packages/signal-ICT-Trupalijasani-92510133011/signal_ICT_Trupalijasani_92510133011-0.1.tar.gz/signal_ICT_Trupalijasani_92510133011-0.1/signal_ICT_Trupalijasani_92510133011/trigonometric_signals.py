import numpy as np
import matplotlib.pyplot as plt

def sine_wave(A, f, phi, t):
    t = np.asarray(t)
    signal = A * np.sin(2 * np.pi * f * t + phi)
    plt.figure()
    plt.plot(t, signal)
    plt.title(f"Sine Wave: A={A}, f={f}Hz, phi={phi}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def cosine_wave(A, f, phi, t):
    t = np.asarray(t)
    signal = A * np.cos(2 * np.pi * f * t + phi)
    plt.figure()
    plt.plot(t, signal)
    plt.title(f"Cosine Wave: A={A}, f={f}Hz, phi={phi}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def exponential_signal(A, a, t):
    t = np.asarray(t)
    signal = A * np.exp(a * t)
    plt.figure()
    plt.plot(t, signal)
    plt.title(f"Exponential Signal: A={A}, a={a}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

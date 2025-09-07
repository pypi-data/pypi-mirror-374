import numpy as np
import matplotlib.pyplot as plt

def time_shift(signal, k):
    signal = np.asarray(signal)
    if k == 0:
        shifted = signal.copy()
    elif k > 0:
        shifted = np.concatenate((np.zeros(k, dtype=signal.dtype), signal))[:len(signal)]
    else:
        kabs = abs(k)
        shifted = np.concatenate((signal[kabs:], np.zeros(kabs, dtype=signal.dtype)))
    n = np.arange(len(signal))
    plt.figure()
    plt.stem(n, signal, markerfmt='bo', label='original')
    plt.stem(n, shifted, markerfmt='ro', label=f'shifted by {k}')
    plt.title(f"Time Shift by {k} units")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    return shifted

def time_scale(signal, k):
    signal = np.asarray(signal)
    if not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer")
    scaled = signal[::k]
    n_orig = np.arange(len(signal))
    n_scaled = np.arange(len(scaled)) * k
    plt.figure()
    plt.stem(n_orig, signal, markerfmt='bo', label='original')
    plt.stem(n_scaled, scaled, markerfmt='ro', label=f'scaled by {k}')
    plt.title(f"Time Scale by factor {k}")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    return scaled

def signal_addition(signal1, signal2):
    s1 = np.asarray(signal1)
    s2 = np.asarray(signal2)
    L = max(len(s1), len(s2))
    s1p = np.pad(s1, (0, L - len(s1)))
    s2p = np.pad(s2, (0, L - len(s2)))
    added = s1p + s2p
    n = np.arange(L)
    plt.figure()
    plt.stem(n, added)
    plt.title("Signal Addition")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return added

def signal_multiplication(signal1, signal2):
    s1 = np.asarray(signal1)
    s2 = np.asarray(signal2)
    L = max(len(s1), len(s2))
    s1p = np.pad(s1, (0, L - len(s1)))
    s2p = np.pad(s2, (0, L - len(s2)))
    mult = s1p * s2p
    n = np.arange(L)
    plt.figure()
    plt.stem(n, mult)
    plt.title("Signal Multiplication")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return mult

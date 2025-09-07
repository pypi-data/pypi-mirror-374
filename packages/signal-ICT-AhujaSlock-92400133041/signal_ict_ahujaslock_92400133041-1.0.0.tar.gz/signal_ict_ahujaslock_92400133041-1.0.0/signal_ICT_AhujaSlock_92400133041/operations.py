import numpy as np
import matplotlib.pyplot as plt

def time_shift(signal, k):
    shifted = np.roll(signal, k)
    plt.stem(shifted)
    plt.title(f'Time Shifted Signal by {k} units')
    plt.xlabel('n')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()
    return shifted

def time_scale(signal, k):
    indices = np.arange(0, len(signal), k)
    scaled = signal[indices]
    plt.stem(scaled)
    plt.title(f'Time Scaled Signal by factor {k}')
    plt.xlabel('n')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()
    return scaled

def signal_addition(signal1, signal2):
    min_len = min(len(signal1), len(signal2))
    result = signal1[:min_len] + signal2[:min_len]
    plt.stem(result)
    plt.title('Signal Addition')
    plt.xlabel('n')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()
    return result

def signal_multiplication(signal1, signal2):
    min_len = min(len(signal1), len(signal2))
    result = signal1[:min_len] * signal2[:min_len]
    plt.stem(result)
    plt.title('Signal Multiplication')
    plt.xlabel('n')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()
    return result

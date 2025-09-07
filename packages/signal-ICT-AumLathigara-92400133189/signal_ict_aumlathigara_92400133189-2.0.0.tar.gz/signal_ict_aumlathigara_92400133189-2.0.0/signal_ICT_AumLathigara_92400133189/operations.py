import numpy as np
import matplotlib.pyplot as plt

def time_shift(signal, k):
    shifted = np.roll(signal, k)  
    plt.plot(signal, label="Original")
    plt.plot(shifted, label=f"Shifted by {k}")
    plt.title("Time Shift Operation")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    return shifted

def time_scale(signal, k):
    scaled = signal[::k] if k > 0 else signal
    plt.plot(signal, label="Original")
    plt.plot(np.arange(0, len(scaled) * k, k), scaled, label=f"Scaled by {k}")
    plt.title("Time Scaling Operation")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    return scaled

def signal_addition(signal1, signal2):
    result = signal1 + signal2
    plt.plot(signal1, label="Signal 1")
    plt.plot(signal2, label="Signal 2")
    plt.plot(result, label="Added Signal")
    plt.title("Signal Addition")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    return result

def signal_multiplication(signal1, signal2):
    result = signal1 * signal2
    plt.plot(signal1, label="Signal 1")
    plt.plot(signal2, label="Signal 2")
    plt.plot(result, label="Multiplied Signal")
    plt.title("Signal Multiplication")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    return result
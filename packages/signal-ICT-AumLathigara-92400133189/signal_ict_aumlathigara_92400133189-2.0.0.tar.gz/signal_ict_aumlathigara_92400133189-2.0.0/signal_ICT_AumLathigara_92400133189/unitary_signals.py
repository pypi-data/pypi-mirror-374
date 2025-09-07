import numpy as np
import matplotlib.pyplot as plt

def unit_step(n):
    signal = np.array([1 if i >=0 else 0 for i  in n])
    plt.stem(n, signal, basefmt=" ")
    plt.title("UNIT STEP")
    plt.xlabel("n")
    plt.ylabel("AMPLITUDE")
    plt.grid()
    plt.show()
    return signal

def unit_impulse(n):
    signal = np.array([1 if i>=0 else 0 for i in n])
    plt.stem(n,signal,basefmt=" ")
    plt.title("UNIT IMPULSE")
    plt.xlabel("n")
    plt.ylabel("AMPLITUDE")
    plt.grid()
    plt.show()
    return signal

def ramp_signal(n):
    signal = np.array([1 if i>=0 else 0 for i in n])
    plt.stem(n,signal,basefmt=" ")
    plt.title("RAMP SIGNAL")
    plt.xlabel("n")
    plt.ylabel("AMPLITUDE")
    plt.grid()
    plt.show()
    return signal
import numpy as np
import matplotlib.pyplot as plt

def sine_wave(A,f,phi,t):
    signal = A*np.sin(2*np.pi*f*t+phi)
    plt.plot(t,signal)
    plt.title("SINE WAVE")
    plt.xlabel(" -TIME- ")
    plt.ylabel("AMPLITUDE")
    plt.grid()
    plt.show()
    return signal


def cosine_wave(A,f,phi,t):
    signal = A*np.cos(2*np.pi*f*t+phi)
    plt.plot(t,signal)
    plt.title("COSINE WAVE")
    plt.xlabel("--TIME")
    plt.ylabel("AMPLITUDE")
    plt.grid()
    plt.show()
    return signal


def exponential_signal(A,a,t):
    signal = A*np.exp(a*t)
    plt.plot(t,signal)
    plt.title("EXPONENTIAL SIGNAL")
    plt.xlabel("Time")
    plt.ylabel("amplitude")
    plt.grid()
    plt.show()
    return signal

import numpy as np
import matplotlib.pyplot as plt

def sine_wave(A: float, f: float, phi: float, t: np.ndarray) -> np.ndarray:
    """
    Generate a sine wave: x(t) = A sin(2π f t + φ).
    Returns the signal and plots it.
    """
    signal = A * np.sin(2 * np.pi * f * t + phi)
    plt.plot(t, signal)
    plt.title("Sine Wave")
    plt.xlabel("t (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def cosine_wave(A: float, f: float, phi: float, t: np.ndarray) -> np.ndarray:
    """
    Generate a cosine wave: x(t) = A cos(2π f t + φ).
    """
    signal = A * np.cos(2 * np.pi * f * t + phi)
    plt.plot(t, signal)
    plt.title("Cosine Wave")
    plt.xlabel("t (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def exponential_signal(A: float, a: float, t: np.ndarray) -> np.ndarray:
    """
    Generate an exponential signal: x(t) = A e^{a t}.
    """
    signal = A * np.exp(a * t)
    plt.plot(t, signal)
    plt.title("Exponential Signal")
    plt.xlabel("t (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

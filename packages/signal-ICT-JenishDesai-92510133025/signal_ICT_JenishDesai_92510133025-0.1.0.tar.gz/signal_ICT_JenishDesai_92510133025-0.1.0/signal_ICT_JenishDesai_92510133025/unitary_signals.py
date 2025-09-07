
import numpy as np
import matplotlib.pyplot as plt

def unit_step(n: np.ndarray) -> np.ndarray:
    """
    Generate a discrete-time unit step signal u[n].
    Args:
        n: numpy array of integer indices
    Returns:
        signal array (same length as n)
    """
    signal = (n >= 0).astype(int)
    plt.stem(n, signal, use_line_collection=True)
    plt.title("Unit Step Signal u[n]")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def unit_impulse(n: np.ndarray) -> np.ndarray:
    """
    Generate a discrete-time unit impulse (Kronecker delta) δ[n].
    Args:
        n: numpy array of integer indices
    Returns:
        signal array (same length as n) with 1 at n==0 else 0
    """
    signal = (n == 0).astype(int)
    plt.stem(n, signal, use_line_collection=True)
    plt.title("Unit Impulse δ[n]")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

def ramp_signal(n: np.ndarray) -> np.ndarray:
    """
    Generate a discrete-time ramp r[n] = n for n>=0 else 0.
    Args:
        n: numpy array of integer indices
    Returns:
        signal array
    """
    signal = np.where(n >= 0, n, 0)
    plt.stem(n, signal, use_line_collection=True)
    plt.title("Ramp Signal r[n]")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return signal

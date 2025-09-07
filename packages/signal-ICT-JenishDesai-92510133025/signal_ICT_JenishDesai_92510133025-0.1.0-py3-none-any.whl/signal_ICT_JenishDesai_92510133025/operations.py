
import numpy as np

def time_shift(signal: np.ndarray, k: int) -> np.ndarray:
    """
    Shift a discrete signal by k samples with zero-padding (no wrap-around).
    Positive k -> delay (shift right), Negative k -> advance (shift left).
    """
    N = len(signal)
    out = np.zeros_like(signal)
    if k >= 0:
        out[k:] = signal[:N-k]
    else:
        out[:N+k] = signal[-k:]
    return out

def time_scale(signal: np.ndarray, k: float) -> np.ndarray:
    """
    Scale the time axis by factor k (resampling to keep same length).
    k > 1 -> compression (faster), 0 < k < 1 -> expansion (slower).
    Uses linear interpolation.
    """
    if k <= 0:
        raise ValueError("k must be > 0")
    N = len(signal)
    n = np.arange(N)
    sample_at = n / k
    left_idx = np.floor(sample_at).astype(int)
    right_idx = np.ceil(sample_at).astype(int)
    frac = sample_at - left_idx
    out = np.zeros(N, dtype=float)
    valid = (left_idx >= 0) & (right_idx < N)
    out[valid] = (1 - frac[valid]) * signal[left_idx[valid]] + frac[valid] * signal[right_idx[valid]]
    exact = (left_idx == right_idx) & (left_idx >= 0) & (left_idx < N)
    out[exact] = signal[left_idx[exact]]
    return out

def signal_addition(signal1: np.ndarray, signal2: np.ndarray) -> np.ndarray:
    """Point-wise addition of two signals of equal length."""
    if len(signal1) != len(signal2):
        raise ValueError("Signals must have the same length for addition.")
    return signal1 + signal2

def signal_multiplication(signal1: np.ndarray, signal2: np.ndarray) -> np.ndarray:
    """Point-wise multiplication of two signals of equal length."""
    if len(signal1) != len(signal2):
        raise ValueError("Signals must have the same length for multiplication.")
    return signal1 * signal2

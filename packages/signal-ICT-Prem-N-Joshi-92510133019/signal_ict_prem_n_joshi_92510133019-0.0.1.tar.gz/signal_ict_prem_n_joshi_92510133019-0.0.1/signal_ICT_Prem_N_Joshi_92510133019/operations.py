import numpy as np
import matplotlib.pyplot as plt

def time_shift(x: np.ndarray, k: int, show: bool = True):
    """Shift a discrete signal by k samples. Output length = input length."""
    n = len(x)
    y = np.zeros_like(x, dtype=float)
    if k >= 0:
        y[k:] = x[:n-k] if k < n else 0
    else:
        k = -k
        y[:n-k] = x[k:] if k < n else 0
    if show:
        _compare_plot(np.arange(n), x, y, title=f"Time Shift by {k} samples", xlabel="n", ylabel="Amplitude", labels=("Original", "Shifted"))
    return y

def time_scale(x: np.ndarray, k: float, show: bool = True):
    """Scale the time axis by factor k using interpolation (length preserved)."""
    if k == 0:
        raise ValueError("k must be non-zero")
    n = len(x)
    idx = np.arange(n)
    src = idx / k
    src_clipped = np.clip(src, 0, n-1)
    y = np.interp(src_clipped, idx, x)
    if show:
        _compare_plot(idx, x, y, title=f"Time Scale by {k}", xlabel="n", ylabel="Amplitude", labels=("Original", "Scaled"))
    return y

def signal_addition(x1: np.ndarray, x2: np.ndarray, show: bool = True):
    """Add two signals (aligned from index 0)."""
    n = min(len(x1), len(x2))
    y = x1[:n] + x2[:n]
    if show:
        _multi_plot(np.arange(n), (x1[:n], x2[:n], y), title="Signal Addition", xlabel="n", ylabel="Amplitude", labels=("x1", "x2", "x1+x2"))
    return y

def signal_multiplication(x1: np.ndarray, x2: np.ndarray, show: bool = True):
    """Multiply two signals pointwise (aligned from index 0)."""
    n = min(len(x1), len(x2))
    y = x1[:n] * x2[:n]
    if show:
        _multi_plot(np.arange(n), (x1[:n], x2[:n], y), title="Signal Multiplication", xlabel="n", ylabel="Amplitude", labels=("x1", "x2", "x1*x2"))
    return y

def _compare_plot(n, x, y, title="", xlabel="", ylabel="", labels=("x","y")):
    plt.figure()
    plt.plot(n, x, label=labels[0])
    plt.plot(n, y, label=labels[1])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

def _multi_plot(n, series, title="", xlabel="", ylabel="", labels=None):
    plt.figure()
    for i, s in enumerate(series):
        if labels and i < len(labels):
            plt.plot(n, s, label=labels[i])
        else:
            plt.plot(n, s)
    if labels:
        plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()

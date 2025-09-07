
import numpy as np
import matplotlib.pyplot as plt

def time_shift(x: np.ndarray, k: int, show: bool = True):
    """
    Shift a discrete signal by k samples.
    Positive k -> right shift (pad on the left with zeros)
    Negative k -> left shift (pad on the right with zeros)
    Returns shifted signal of the SAME length as input.
    """
    n = len(x)
    y = np.zeros_like(x, dtype=float)
    if k >= 0:
        y[k:] = x[:n-k] if k < n else 0
    else:
        k = -k
        y[:n-k] = x[k:] if k < n else 0
    if show:
        _compare_plot(np.arange(n), x, y, title=f"Time Shift by {k if isinstance(k,int) else k} samples", xlabel="n", ylabel="amplitude", labels=("original", "shifted"))
    return y

def time_scale(x: np.ndarray, k: float, show: bool = True):
    """
    Scale the time axis by factor k using interpolation so output length equals input length.
    k>1 compresses (faster), k<1 expands (slower).
    """
    if k == 0:
        raise ValueError("k must be non-zero")
    n = len(x)
    idx = np.arange(n)
    # new signal y[n] corresponds to x[n/k] (with interpolation)
    src = idx / k
    src_clipped = np.clip(src, 0, n-1)
    y = np.interp(src_clipped, idx, x)
    if show:
        _compare_plot(idx, x, y, title=f"Time Scale by factor {k}", xlabel="n", ylabel="amplitude", labels=("original", "scaled"))
    return y

def signal_addition(x1: np.ndarray, x2: np.ndarray, show: bool = True):
    """
    Add two signals (aligned from index 0). If lengths differ, operate on min length.
    """
    n = min(len(x1), len(x2))
    y = x1[:n] + x2[:n]
    if show:
        _multi_plot(np.arange(n), (x1[:n], x2[:n], y), title="Signal Addition", xlabel="n", ylabel="amplitude", labels=("x1", "x2", "x1 + x2"))
    return y

def signal_multiplication(x1: np.ndarray, x2: np.ndarray, show: bool = True):
    """
    Point-wise multiply two signals (aligned from index 0). If lengths differ, operate on min length.
    """
    n = min(len(x1), len(x2))
    y = x1[:n] * x2[:n]
    if show:
        _multi_plot(np.arange(n), (x1[:n], x2[:n], y), title="Signal Multiplication", xlabel="n", ylabel="amplitude", labels=("x1", "x2", "x1 * x2"))
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

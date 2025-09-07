import numpy as np
import matplotlib.pyplot as plt

def unit_step(n: int, show: bool = True):
    """Generates a unit step sequence u[n] of length n."""
    if n <= 0:
        raise ValueError("n must be positive")
    x = np.ones(n, dtype=float)
    if show:
        _stem(np.arange(n), x, title=f"Unit Step u[n]", xlabel="n", ylabel="Amplitude")
    return x

def unit_impulse(n: int, k: int = 0, show: bool = True):
    """Generates a unit impulse δ[n-k] of length n with impulse at index k."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not (0 <= k < n):
        raise ValueError("k must be in [0, n-1]")
    x = np.zeros(n, dtype=float)
    x[k] = 1.0
    if show:
        _stem(np.arange(n), x, title=f"Unit Impulse δ[n-{k}]", xlabel="n", ylabel="Amplitude")
    return x

def ramp_signal(n: int, show: bool = True):
    """Generates a discrete-time ramp r[n] = n for n in [0, n-1]."""
    if n <= 0:
        raise ValueError("n must be positive")
    x = np.arange(n, dtype=float)
    if show:
        _stem(np.arange(n), x, title=f"Ramp r[n]", xlabel="n", ylabel="Amplitude")
    return x

def _stem(n, x, title="", xlabel="", ylabel=""):
    plt.figure()
    plt.stem(n, x)   # ✅ removed use_line_collection for compatibility
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()

import numpy as np
import matplotlib.pyplot as plt

def sine_wave(A: float, f: float, phi: float, t: np.ndarray, show: bool = True):
    """s(t) = A * sin(2π f t + phi)"""
    x = A * np.sin(2 * np.pi * f * t + phi)
    if show:
        _plot(t, x, title=f"Sine: A={A}, f={f}Hz, phi={phi}", xlabel="t (s)", ylabel="Amplitude")
    return x

def cosine_wave(A: float, f: float, phi: float, t: np.ndarray, show: bool = True):
    """c(t) = A * cos(2π f t + phi)"""
    x = A * np.cos(2 * np.pi * f * t + phi)
    if show:
        _plot(t, x, title=f"Cosine: A={A}, f={f}Hz, phi={phi}", xlabel="t (s)", ylabel="Amplitude")
    return x

def exponential_signal(A: float, a: float, t: np.ndarray, show: bool = True):
    """e(t) = A * exp(a t)"""
    x = A * np.exp(a * t)
    if show:
        _plot(t, x, title=f"Exponential: A={A}, a={a}", xlabel="t (s)", ylabel="Amplitude")
    return x

def _plot(t, x, title="", xlabel="", ylabel=""):
    plt.figure()
    plt.plot(t, x)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()

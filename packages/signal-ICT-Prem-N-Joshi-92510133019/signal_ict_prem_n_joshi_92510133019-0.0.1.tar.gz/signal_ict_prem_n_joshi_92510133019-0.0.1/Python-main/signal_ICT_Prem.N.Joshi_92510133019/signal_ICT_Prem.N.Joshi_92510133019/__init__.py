
"""
signal_ICT_Prem.N.Joshi_92510133019
A teaching package for basic signal generation and operations.
"""

from .unitary_signals import unit_step, unit_impulse, ramp_signal
from .trigonometric_signals import sine_wave, cosine_wave, exponential_signal
from .operations import time_shift, time_scale, signal_addition, signal_multiplication

__all__ = [
    "unit_step", "unit_impulse", "ramp_signal",
    "sine_wave", "cosine_wave", "exponential_signal",
    "time_shift", "time_scale", "signal_addition", "signal_multiplication"
]

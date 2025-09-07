"""
Package: signal_ICT_Prem_N_Joshi_92510133019
Basic signals and operations for ICT course.
"""

from . import unitary_signals
from . import trigonometric_signals
from . import operations

# ✅ Direct imports for convenience
from .unitary_signals import unit_step, unit_impulse, ramp_signal
from .trigonometric_signals import sine_wave, cosine_wave, exponential_signal
from .operations import time_shift, time_scale, signal_addition, signal_multiplication

__all__ = [
    "unitary_signals",
    "trigonometric_signals",
    "operations",
    "unit_step", "unit_impulse", "ramp_signal",
    "sine_wave", "cosine_wave", "exponential_signal",
    "time_shift", "time_scale", "signal_addition", "signal_multiplication"
]

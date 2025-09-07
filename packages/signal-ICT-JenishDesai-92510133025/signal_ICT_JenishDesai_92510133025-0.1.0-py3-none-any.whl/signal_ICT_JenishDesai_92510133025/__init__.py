"""Signal package for LHC exam.

Student: Jenish Desai
Enrollment: 92510133025

Modules:
    - unitary_signals: unit_step, unit_impulse, ramp_signal
    - trigonometric_signals: sine_wave, cosine_wave, exponential_signal
    - operations: time_shift, time_scale, signal_addition, signal_multiplication
"""

from .unitary_signals import unit_step, unit_impulse, ramp_signal
from .trigonometric_signals import sine_wave, cosine_wave, exponential_signal
from .operations import time_shift, time_scale, signal_addition, signal_multiplication

__all__ = [
    "unit_step", "unit_impulse", "ramp_signal",
    "sine_wave", "cosine_wave", "exponential_signal",
    "time_shift", "time_scale", "signal_addition", "signal_multiplication"
]

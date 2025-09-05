"""
Wave and oscillation utilities in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK
import math


# --- Basic wave relationships ---

def wave_speed(frequency_hz: float, wavelength_voxels: float) -> float:
    """
    Compute wave speed in m/s.

    Args:
        frequency_hz: frequency in Hertz (1/s)
        wavelength_voxels: wavelength in voxels

    Returns:
        Wave speed (m/s)
    """
    wavelength_m = wavelength_voxels * VOXEL_SIZE_M
    return frequency_hz * wavelength_m


def frequency_from_period(period_ticks: float) -> float:
    """
    Compute frequency from period in ticks.

    Args:
        period_ticks: period in ticks

    Returns:
        Frequency (Hz)
    """
    period_s = period_ticks * SECONDS_PER_TICK
    return 1.0 / period_s if period_s > 0 else float("inf")


def period_from_frequency(frequency_hz: float) -> float:
    """
    Compute period in seconds from frequency.

    Args:
        frequency_hz: frequency in Hz

    Returns:
        Period (seconds)
    """
    return 1.0 / frequency_hz if frequency_hz > 0 else float("inf")


# --- Oscillators ---

def simple_harmonic_displacement(amplitude_voxels: float, frequency_hz: float, t_ticks: float) -> float:
    """
    Compute displacement of a simple harmonic oscillator at time t.

    Args:
        amplitude_voxels: maximum displacement (voxels)
        frequency_hz: frequency in Hz
        t_ticks: time in ticks

    Returns:
        Displacement (voxels)
    """
    t_s = t_ticks * SECONDS_PER_TICK
    return amplitude_voxels * math.cos(2 * math.pi * frequency_hz * t_s)


def angular_frequency(frequency_hz: float) -> float:
    """
    Compute angular frequency (rad/s).

    Args:
        frequency_hz: frequency in Hz

    Returns:
        Angular frequency (rad/s)
    """
    return 2 * math.pi * frequency_hz


__all__ = [
    "wave_speed",
    "frequency_from_period",
    "period_from_frequency",
    "simple_harmonic_displacement",
    "angular_frequency",
]
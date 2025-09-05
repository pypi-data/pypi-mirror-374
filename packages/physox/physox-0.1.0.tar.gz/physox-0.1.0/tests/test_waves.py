import math
import pytest
from physox.waves import (
    wave_speed,
    frequency_from_period,
    period_from_frequency,
    simple_harmonic_displacement,
    angular_frequency,
)

def test_wave_speed():
    # 10 Hz wave, wavelength 1000 voxels (1 mm)
    v = wave_speed(10, 1000)
    assert math.isclose(v, 0.01, rel_tol=1e-6)  # m/s

def test_frequency_from_period():
    f = frequency_from_period(100)  # 100 ticks = 100s
    assert math.isclose(f, 0.01, rel_tol=1e-6)

def test_frequency_from_period_zero():
    assert frequency_from_period(0) == float("inf")


def test_period_from_frequency():
    T = period_from_frequency(2.0)  # 2 Hz
    assert math.isclose(T, 0.5, rel_tol=1e-6)

def test_simple_harmonic_displacement():
    # amplitude 10 vox, f=1 Hz, t=0 -> cos(0)=1
    d0 = simple_harmonic_displacement(10, 1.0, 0)
    assert math.isclose(d0, 10.0, rel_tol=1e-6)

    # at quarter period, cos(pi/2)=0
    quarter_T = 0.25 / 1.0  # quarter second at 1 Hz
    d_quarter = simple_harmonic_displacement(10, 1.0, quarter_T)
    assert math.isclose(d_quarter, 0.0, abs_tol=1e-6)

def test_angular_frequency():
    omega = angular_frequency(1.0)  # 1 Hz
    assert math.isclose(omega, 2 * math.pi, rel_tol=1e-6)

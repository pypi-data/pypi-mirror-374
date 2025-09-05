import pytest
from physox.momentum import momentum, impulse, velocity_from_momentum


def test_momentum_zero_velocity():
    assert momentum(10.0, 0.0) == pytest.approx(0.0)


def test_momentum_basic():
    # 1 kg object moving at 1 voxel/tick
    p = momentum(1.0, 1.0)
    assert p > 0
    # Round-trip check
    v = velocity_from_momentum(p, 1.0)
    assert v == pytest.approx(1.0, rel=1e-6)


def test_impulse_zero_force():
    assert impulse(0.0, 10) == pytest.approx(0.0)


def test_impulse_basic():
    # Impulse = F * Δt
    j = impulse(5.0, 2)
    assert j == pytest.approx(10.0)


def test_velocity_from_momentum():
    p = 20.0  # kg·m/s
    mass = 10.0
    v = velocity_from_momentum(p, mass)
    # Should scale back consistently
    assert v > 0
    assert pytest.approx(momentum(mass, v), rel=1e-6) == p

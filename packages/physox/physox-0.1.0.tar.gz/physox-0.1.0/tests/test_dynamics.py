import pytest
from physox.dynamics import (
    acceleration_from_force,
    force_from_acceleration,
    apply_force,
    displacement_under_force,
)
from physox.constants import VOXEL_SIZE_M, SECONDS_PER_TICK

def test_acceleration_force_roundtrip():
    mass = 1.0  # kg
    force = 10.0  # N

    # Convert to voxels/tick²
    a_vox = acceleration_from_force(force, mass)

    # Convert back to force
    force_back = force_from_acceleration(a_vox, mass)

    assert pytest.approx(force, rel=1e-9) == force_back

def test_apply_force_updates_velocity():
    mass = 2.0  # kg
    force = 4.0  # N
    v0 = 0.0  # voxels/tick
    t = 10  # ticks

    v_final = apply_force(v0, force, mass, t)

    # a = F/m = 2 m/s²
    # in voxel units:
    a_vox = acceleration_from_force(force, mass)
    expected = v0 + a_vox * t

    assert pytest.approx(expected, rel=1e-9) == v_final

def test_displacement_under_force():
    mass = 1.0  # kg
    force = 1.0  # N
    v0 = 0.0
    t = 5

    d_vox = displacement_under_force(v0, force, mass, t)

    # check scaling: should be positive and proportional to t²
    d2 = displacement_under_force(v0, force, mass, 2 * t)

    assert d_vox > 0
    assert d2 > d_vox
    assert pytest.approx(d2, rel=0.01) == 4 * d_vox  # quadratic scaling

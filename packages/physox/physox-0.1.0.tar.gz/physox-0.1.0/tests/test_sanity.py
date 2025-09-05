"""
Sanity suite for physox.
Quick checks to ensure the package installs and core functions work.
"""

import physox


def test_constants_exist():
    # Speed of light is correct
    assert physox.C_M_PER_S == 299_792_458


def test_kinematics_displacement():
    from physox.kinematics import displacement_voxels
    d = displacement_voxels(1.0, 0.0, 10)  # 1 voxel/tick for 10 ticks
    assert d == 10.0


def test_velocity_update():
    from physox.kinematics import velocity_voxels
    v = velocity_voxels(5.0, 2.0, 3)  # v0=5, a=2, t=3
    assert v == 11.0


def test_energy_kinetic():
    from physox.energy import kinetic_energy
    ke = kinetic_energy(1.0, 1.0)  # 1 kg, 1 voxel/s
    assert ke > 0


def test_gravity_force():
    from physox.gravity import gravitational_force
    f = gravitational_force(1.0, 1.0, 1e6)  # masses 1 kg each, ~1 m apart
    assert f > 0

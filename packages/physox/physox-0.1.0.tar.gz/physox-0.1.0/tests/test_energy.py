# tests/test_energy.py

import math
import pytest
from physox.energy import (
    kinetic_energy,
    gravitational_potential_energy,
    thermal_energy,
    joules_to_electronvolts,
    electronvolts_to_joules,
)
from physox.constants import VOXEL_SIZE_M, G_M3_PER_KG_S2


def test_kinetic_energy():
    m = 1.0  # 1 kg
    v_vox = 10 / VOXEL_SIZE_M  # 10 m/s expressed in voxels/tick
    ke = kinetic_energy(m, v_vox)
    assert math.isclose(ke, 0.5 * m * (10 ** 2), rel_tol=1e-9)


def test_gravitational_potential_energy():
    m1, m2 = 1.0, 2.0
    r_m = 10.0
    r_vox = r_m / VOXEL_SIZE_M
    pe = gravitational_potential_energy(m1, m2, r_vox)
    expected = -G_M3_PER_KG_S2 * m1 * m2 / r_m
    assert math.isclose(pe, expected, rel_tol=1e-9)


def test_thermal_energy():
    moles = 1.0
    T = 300.0  # room temp
    E = thermal_energy(moles, T)
    expected = 1.5 * moles * 8.314 * T
    assert math.isclose(E, expected, rel_tol=1e-9)


def test_energy_conversions():
    J = 1.0
    ev = joules_to_electronvolts(J)
    J_back = electronvolts_to_joules(ev)
    assert math.isclose(J, J_back, rel_tol=1e-12)

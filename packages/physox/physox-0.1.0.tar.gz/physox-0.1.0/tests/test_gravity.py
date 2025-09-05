import math
import pytest
from physox.gravity import gravitational_force, gravitational_field, potential_energy
from physox.constants import VOXEL_SIZE_M, G_M3_PER_KG_S2


def test_gravitational_force_symmetry():
    m = 1.0
    r_m = 1.0
    r_vox = r_m / VOXEL_SIZE_M
    f = gravitational_force(m, m, r_vox)
    expected = G_M3_PER_KG_S2 * m * m / (r_m ** 2)
    assert math.isclose(f, expected, rel_tol=1e-12)


def test_field_and_energy_relation():
    m1 = 5.97e24  # Earth mass
    m2 = 1.0      # test particle
    r_m = 6.371e6
    r_vox = r_m / VOXEL_SIZE_M

    g = gravitational_field(m1, r_vox)
    U = potential_energy(m1, m2, r_vox)

    # Field should be derivative of potential: g ≈ |U| / (m2 * r_m)
    assert math.isclose(g, abs(U) / (m2 * r_m), rel_tol=1e-12)


def test_division_by_zero():
    with pytest.raises(ValueError):
        gravitational_force(1.0, 1.0, 0)
    with pytest.raises(ValueError):
        gravitational_field(1.0, 0)
    with pytest.raises(ValueError):
        potential_energy(1.0, 1.0, 0)

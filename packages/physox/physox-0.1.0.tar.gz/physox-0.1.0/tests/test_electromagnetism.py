import math
import pytest
from physox.electromagnetism import coulomb_force, electric_field, potential_energy
from physox.constants import VOXEL_SIZE_M


def test_coulomb_force_symmetry():
    q = 1e-6  # 1 µC
    r_m = 1.0
    r_vox = r_m / VOXEL_SIZE_M
    f1 = coulomb_force(q, q, r_vox)
    f2 = coulomb_force(-q, -q, r_vox)
    assert math.isclose(f1, f2, rel_tol=1e-12)


def test_electric_field_and_potential():
    q = 1e-6  # 1 µC
    r_m = 1.0
    r_vox = r_m / VOXEL_SIZE_M
    E = electric_field(q, r_vox)
    V = potential_energy(q, q, r_vox) / q  # potential per unit charge
    assert math.isclose(E, V / r_m, rel_tol=1e-12)


def test_division_by_zero():
    with pytest.raises(ValueError):
        coulomb_force(1.0, 1.0, 0)
    with pytest.raises(ValueError):
        electric_field(1.0, 0)
    with pytest.raises(ValueError):
        potential_energy(1.0, 1.0, 0)

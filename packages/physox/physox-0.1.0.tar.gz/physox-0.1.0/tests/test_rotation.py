import math
import pytest
from physox.rotation import (
    angular_displacement,
    angular_velocity,
    torque,
    moment_of_inertia,
    rotational_kinetic_energy,
)


def test_angular_displacement_basic():
    theta = angular_displacement(theta0=0, omega=1.0, alpha=0.5, t_ticks=2)
    # θ = 0 + 1*2 + 0.5*0.5*2^2 = 2 + 1 = 3
    assert math.isclose(theta, 3.0, rel_tol=1e-9)


def test_angular_velocity():
    omega = angular_velocity(omega0=2.0, alpha=0.5, t_ticks=4)
    # ω = 2 + 0.5*4 = 4
    assert math.isclose(omega, 4.0, rel_tol=1e-9)


def test_torque():
    τ = torque(force_N=10, radius_voxels=1e6)  # 1 m lever arm
    # τ = 10 * 1 = 10
    assert math.isclose(τ, 10.0, rel_tol=1e-9)


@pytest.mark.parametrize("shape,expected_factor", [
    ("solid_sphere", 0.4),
    ("hollow_sphere", 2/3),
    ("solid_cylinder", 0.5),
])
def test_moment_of_inertia_shapes(shape, expected_factor):
    m = 2.0
    r_vox = 1e6  # 1 m
    I = moment_of_inertia(shape, m, r_vox)
    expected = expected_factor * m * (1.0**2)
    assert math.isclose(I, expected, rel_tol=1e-9)


def test_moment_of_inertia_rods():
    m = 1.0
    L_vox = 2e6  # 2 m
    I_center = moment_of_inertia("rod_center", m, radius_voxels=0, length_voxels=L_vox)
    I_end = moment_of_inertia("rod_end", m, radius_voxels=0, length_voxels=L_vox)
    assert math.isclose(I_center, (1/12) * m * (2**2), rel_tol=1e-9)
    assert math.isclose(I_end, (1/3) * m * (2**2), rel_tol=1e-9)


def test_rotational_kinetic_energy():
    I = 2.0
    omega = 3.0
    KE = rotational_kinetic_energy(I, omega)
    assert math.isclose(KE, 0.5 * I * omega**2, rel_tol=1e-9)

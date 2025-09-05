"""
Gravitational forces and energy in voxel space.
"""

from .constants import VOXEL_SIZE_M, G_M3_PER_KG_S2


def gravitational_force(m1_kg: float, m2_kg: float, r_voxels: float) -> float:
    """
    Compute gravitational force (N) between two masses.

    Args:
        m1_kg (float): mass 1 in kilograms
        m2_kg (float): mass 2 in kilograms
        r_voxels (float): distance between masses in voxels

    Returns:
        float: force in Newtons
    """
    r_m = r_voxels * VOXEL_SIZE_M
    if r_m == 0:
        raise ValueError("Distance cannot be zero.")
    return G_M3_PER_KG_S2 * m1_kg * m2_kg / (r_m ** 2)


def gravitational_field(mass_kg: float, r_voxels: float) -> float:
    """
    Compute gravitational field (acceleration, m/s²) at distance r from a point mass.

    Args:
        mass_kg (float): mass in kilograms
        r_voxels (float): distance in voxels

    Returns:
        float: acceleration in m/s²
    """
    r_m = r_voxels * VOXEL_SIZE_M
    if r_m == 0:
        raise ValueError("Distance cannot be zero.")
    return G_M3_PER_KG_S2 * mass_kg / (r_m ** 2)


def potential_energy(m1_kg: float, m2_kg: float, r_voxels: float) -> float:
    """
    Gravitational potential energy (Joules).

    Args:
        m1_kg (float): mass 1 in kilograms
        m2_kg (float): mass 2 in kilograms
        r_voxels (float): separation in voxels

    Returns:
        float: potential energy in Joules (negative for bound systems)
    """
    r_m = r_voxels * VOXEL_SIZE_M
    if r_m == 0:
        raise ValueError("Distance cannot be zero.")
    return -G_M3_PER_KG_S2 * m1_kg * m2_kg / r_m


__all__ = [
    "gravitational_force",
    "gravitational_field",
    "potential_energy",
]
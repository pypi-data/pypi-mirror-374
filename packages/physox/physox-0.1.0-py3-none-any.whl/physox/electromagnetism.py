"""
Electromagnetic forces and energy in voxel space.
"""

from .constants import VOXEL_SIZE_M

# Coulomb's constant (SI)
K_COULOMB = 8.9875517923e9  # N·m²/C²


def coulomb_force(q1_C: float, q2_C: float, r_voxels: float) -> float:
    """
    Compute electrostatic force (N) between two charges.

    Args:
        q1_C (float): charge 1 in coulombs
        q2_C (float): charge 2 in coulombs
        r_voxels (float): distance between charges in voxels

    Returns:
        float: force in newtons
    """
    r_m = r_voxels * VOXEL_SIZE_M
    if r_m == 0:
        raise ValueError("Distance cannot be zero.")
    return K_COULOMB * q1_C * q2_C / (r_m ** 2)


def electric_field(q_C: float, r_voxels: float) -> float:
    """
    Compute electric field (N/C) at a distance r from a point charge.

    Args:
        q_C (float): point charge in coulombs
        r_voxels (float): distance from charge in voxels

    Returns:
        float: field strength in N/C
    """
    r_m = r_voxels * VOXEL_SIZE_M
    if r_m == 0:
        raise ValueError("Distance cannot be zero.")
    return K_COULOMB * q_C / (r_m ** 2)


def potential_energy(q1_C: float, q2_C: float, r_voxels: float) -> float:
    """
    Compute electrostatic potential energy (Joules).

    Args:
        q1_C (float): charge 1 in coulombs
        q2_C (float): charge 2 in coulombs
        r_voxels (float): separation in voxels

    Returns:
        float: potential energy in Joules
    """
    r_m = r_voxels * VOXEL_SIZE_M
    if r_m == 0:
        raise ValueError("Distance cannot be zero.")
    return K_COULOMB * q1_C * q2_C / r_m


__all__ = [
    "coulomb_force",
    "electric_field",
    "potential_energy",
]
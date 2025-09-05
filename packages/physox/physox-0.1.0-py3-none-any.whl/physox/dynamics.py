"""
Dynamics in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK

# --- Conversions ---

def acceleration_from_force(force_N: float, mass_kg: float) -> float:
    """
    Compute acceleration in voxels/tick² from a force and mass.

    Args:
        force_N: force in Newtons (kg·m/s²)
        mass_kg: mass in kilograms

    Returns:
        float: acceleration in voxels/tick²
    """
    a_m_s2 = force_N / mass_kg
    return (a_m_s2 * SECONDS_PER_TICK**2) / VOXEL_SIZE_M


def force_from_acceleration(a_voxels: float, mass_kg: float) -> float:
    """
    Compute force (N) from acceleration in voxels/tick² and mass in kg.
    """
    a_m_s2 = (a_voxels * VOXEL_SIZE_M) / (SECONDS_PER_TICK**2)
    return mass_kg * a_m_s2


# --- Applications ---

def apply_force(v0_vox: float, force_N: float, mass_kg: float, t_ticks: int) -> float:
    """
    Update velocity after applying a constant force for t_ticks.

    Args:
        v0_vox: initial velocity in voxels/tick
        force_N: force in Newtons
        mass_kg: object mass in kg
        t_ticks: number of ticks force is applied

    Returns:
        float: new velocity in voxels/tick
    """
    a = acceleration_from_force(force_N, mass_kg)
    return v0_vox + a * t_ticks


def displacement_under_force(v0_vox: float, force_N: float, mass_kg: float, t_ticks: int) -> float:
    """
    Compute displacement (voxels) under constant force.

    Args:
        v0_vox: initial velocity in voxels/tick
        force_N: force in Newtons
        mass_kg: object mass in kg
        t_ticks: number of ticks force is applied

    Returns:
        float: displacement in voxels
    """
    a = acceleration_from_force(force_N, mass_kg)
    return v0_vox * t_ticks + 0.5 * a * (t_ticks ** 2)

__all__ = [
    "acceleration_from_force",
    "force_from_acceleration",
    "apply_force",
    "displacement_under_force",
]
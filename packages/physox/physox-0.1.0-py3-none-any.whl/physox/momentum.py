"""
Momentum utilities in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK


def momentum(mass_kg: float, velocity_voxels_per_tick: float) -> float:
    """
    Compute linear momentum (kg·m/s) from mass and velocity in voxel units.

    Args:
        mass_kg (float): mass of the body (kg)
        velocity_voxels_per_tick (float): velocity in voxels/tick

    Returns:
        float: momentum in kg·m/s
    """
    v_m_per_s = velocity_voxels_per_tick * (VOXEL_SIZE_M / SECONDS_PER_TICK)
    return mass_kg * v_m_per_s


def impulse(force_N: float, duration_ticks: int) -> float:
    """
    Compute impulse (N·s = change in momentum) given a force and time.

    Args:
        force_N (float): applied force (N)
        duration_ticks (int): duration (ticks)

    Returns:
        float: impulse in N·s (equivalent to kg·m/s)
    """
    dt = duration_ticks * SECONDS_PER_TICK
    return force_N * dt


def velocity_from_momentum(momentum_si: float, mass_kg: float) -> float:
    """
    Convert momentum back into velocity in voxels/tick.

    Args:
        momentum_si (float): momentum in kg·m/s
        mass_kg (float): mass (kg)

    Returns:
        float: velocity in voxels/tick
    """
    v_m_per_s = momentum_si / mass_kg
    return v_m_per_s / (VOXEL_SIZE_M / SECONDS_PER_TICK)


__all__ = [
    "momentum",
    "impulse",
    "velocity_from_momentum",
]
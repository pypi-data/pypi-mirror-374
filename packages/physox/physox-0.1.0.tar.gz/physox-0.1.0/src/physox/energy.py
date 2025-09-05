"""
Energy functions in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK, G_M3_PER_KG_S2

# --- Kinetic energy ---

def kinetic_energy(mass_kg: float, velocity_voxels_per_tick: float) -> float:
    """
    Compute kinetic energy in Joules.
    
    Args:
        mass_kg: mass of the object
        velocity_voxels_per_tick: velocity in voxels/tick

    Returns:
        Kinetic energy (Joules)
    """
    v_m_s = velocity_voxels_per_tick * (VOXEL_SIZE_M / SECONDS_PER_TICK)
    return 0.5 * mass_kg * (v_m_s ** 2)


# --- Potential energy ---

def gravitational_potential_energy(mass_kg: float, other_mass_kg: float, distance_voxels: float) -> float:
    """
    Compute gravitational potential energy between two masses.

    Args:
        mass_kg: mass of first object
        other_mass_kg: mass of second object
        distance_voxels: distance between them in voxels

    Returns:
        Gravitational potential energy (Joules, negative value)
    """
    r_m = distance_voxels * VOXEL_SIZE_M
    return -G_M3_PER_KG_S2 * mass_kg * other_mass_kg / r_m if r_m > 0 else float("-inf")


# --- Thermal energy (idealized) ---

def thermal_energy(moles: float, temperature_K: float) -> float:
    """
    Estimate thermal energy using ideal gas approximation.
    
    Args:
        moles: number of moles
        temperature_K: temperature in Kelvin

    Returns:
        Thermal energy (Joules)
    """
    R = 8.314  # J/(mol·K)
    return 1.5 * moles * R * temperature_K


# --- Energy conversions ---

def joules_to_electronvolts(joules: float) -> float:
    """
    Convert Joules → electronvolts.
    """
    eV = 1.602176634e-19
    return joules / eV


def electronvolts_to_joules(ev: float) -> float:
    """
    Convert electronvolts → Joules.
    """
    eV = 1.602176634e-19
    return ev * eV


__all__ = [
    "kinetic_energy",
    "gravitational_potential_energy",
    "thermal_energy",
    "joules_to_electronvolts",
    "electronvolts_to_joules",
]
"""
Rotation dynamics in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK
import math


# --- Angular kinematics ---

def angular_displacement(theta0: float, omega: float, alpha: float, t_ticks: int) -> float:
    """
    Compute angular displacement (radians).
    
    Args:
        theta0: initial angle (rad)
        omega: initial angular velocity (rad/tick)
        alpha: angular acceleration (rad/tick²)
        t_ticks: time elapsed (ticks)
    """
    return theta0 + omega * t_ticks + 0.5 * alpha * (t_ticks ** 2)


def angular_velocity(omega0: float, alpha: float, t_ticks: int) -> float:
    """
    Angular velocity (rad/tick).
    """
    return omega0 + alpha * t_ticks


# --- Torque and inertia ---

def torque(force_N: float, radius_voxels: float) -> float:
    """
    Torque τ = r × F (N·m).
    
    Args:
        force_N: applied force (Newtons)
        radius_voxels: lever arm in voxels
    """
    r_m = radius_voxels * VOXEL_SIZE_M
    return force_N * r_m


def moment_of_inertia(shape: str, mass_kg: float, radius_voxels: float, length_voxels: float = None) -> float:
    """
    Approximate moment of inertia for common shapes.
    
    Supported shapes:
    - 'solid_sphere': I = 2/5 m r²
    - 'hollow_sphere': I = 2/3 m r²
    - 'solid_cylinder': I = 1/2 m r²
    - 'rod_center': I = 1/12 m L²
    - 'rod_end': I = 1/3 m L²
    
    Args:
        shape: type of shape
        mass_kg: mass
        radius_voxels: radius in voxels (or thickness for rods)
        length_voxels: length in voxels (needed for rods)
    """
    r_m = radius_voxels * VOXEL_SIZE_M
    L_m = length_voxels * VOXEL_SIZE_M if length_voxels else None

    if shape == "solid_sphere":
        return 0.4 * mass_kg * r_m**2
    elif shape == "hollow_sphere":
        return (2/3) * mass_kg * r_m**2
    elif shape == "solid_cylinder":
        return 0.5 * mass_kg * r_m**2
    elif shape == "rod_center" and L_m:
        return (1/12) * mass_kg * L_m**2
    elif shape == "rod_end" and L_m:
        return (1/3) * mass_kg * L_m**2
    else:
        raise ValueError("Unsupported shape or missing parameter")


# --- Rotational energy ---

def rotational_kinetic_energy(I: float, omega: float) -> float:
    """
    Rotational kinetic energy (J).
    
    Args:
        I: moment of inertia (kg·m²)
        omega: angular velocity (rad/s)
    """
    return 0.5 * I * omega**2


__all__ = [
    "angular_displacement",
    "angular_velocity",
    "torque",
    "moment_of_inertia",
    "rotational_kinetic_energy",
]
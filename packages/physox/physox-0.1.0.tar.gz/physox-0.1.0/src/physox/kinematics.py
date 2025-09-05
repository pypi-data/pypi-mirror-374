"""
Kinematics in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK


# --- Core kinematics in voxel-space ---
def displacement_voxels(v0: float, a: float, t_ticks: int) -> float:
    """Displacement in voxels under constant acceleration."""
    return v0 * t_ticks + 0.5 * a * (t_ticks ** 2)


def velocity_voxels(v0: float, a: float, t_ticks: int) -> float:
    """Velocity in voxels/tick after t_ticks."""
    return v0 + a * t_ticks


def velocity(distance_voxels: int, time_ticks: int) -> float:
    """Velocity in voxels/tick from displacement and time."""
    if time_ticks == 0:
        raise ZeroDivisionError("Time interval cannot be zero.")
    return distance_voxels / time_ticks


def acceleration(v1_vox: float, v2_vox: float, time_ticks: int) -> float:
    """Acceleration in voxels/tick² from Δv and time."""
    if time_ticks == 0:
        raise ZeroDivisionError("Time interval cannot be zero.")
    return (v2_vox - v1_vox) / time_ticks


# --- Converters to SI units ---
def to_meters(voxels: float) -> float:
    """Convert voxel displacement to meters."""
    return voxels * VOXEL_SIZE_M


def to_seconds(t_ticks: int) -> float:
    """Convert ticks to seconds."""
    return t_ticks * SECONDS_PER_TICK


def velocity_mps(distance_voxels: int, time_ticks: int) -> float:
    """Velocity in m/s from voxels and ticks."""
    return velocity(distance_voxels, time_ticks) * VOXEL_SIZE_M / SECONDS_PER_TICK


def acceleration_mps2(v1_mps: float, v2_mps: float, time_ticks: int) -> float:
    """Acceleration in m/s² from Δv and ticks."""
    if time_ticks == 0:
        raise ZeroDivisionError("Time interval cannot be zero.")
    return (v2_mps - v1_mps) / (time_ticks * SECONDS_PER_TICK)

__all__ = [
    "displacement_voxels",
    "velocity_voxels",
    "velocity",
    "acceleration",
    "to_meters",
    "to_seconds",
    "velocity_mps",
    "acceleration_mps2",
]

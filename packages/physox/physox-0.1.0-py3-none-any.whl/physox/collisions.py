"""
Collisions in voxel space.
"""

from .constants import VOXEL_SIZE_M, SECONDS_PER_TICK


def elastic_collision_1d(m1: float, v1_vox: float, m2: float, v2_vox: float):
    """
    Compute final velocities (1D elastic collision).
    
    Args:
        m1 (float): mass of first body (kg)
        v1_vox (float): initial velocity of first body (voxels/tick)
        m2 (float): mass of second body (kg)
        v2_vox (float): initial velocity of second body (voxels/tick)

    Returns:
        (v1f, v2f): final velocities in voxels/tick
    """
    # Convert to m/s
    v1 = v1_vox * (VOXEL_SIZE_M / SECONDS_PER_TICK)
    v2 = v2_vox * (VOXEL_SIZE_M / SECONDS_PER_TICK)

    v1f = ((m1 - m2) / (m1 + m2)) * v1 + (2 * m2 / (m1 + m2)) * v2
    v2f = (2 * m1 / (m1 + m2)) * v1 + ((m2 - m1) / (m1 + m2)) * v2

    # Convert back to voxels/tick
    scale = SECONDS_PER_TICK / VOXEL_SIZE_M
    return v1f * scale, v2f * scale


def inelastic_collision_1d(m1: float, v1_vox: float, m2: float, v2_vox: float):
    """
    Compute final velocity for perfectly inelastic collision (1D).
    Bodies stick together.

    Args:
        m1 (float): mass of first body (kg)
        v1_vox (float): initial velocity of first body (voxels/tick)
        m2 (float): mass of second body (kg)
        v2_vox (float): initial velocity of second body (voxels/tick)

    Returns:
        v_final: shared velocity in voxels/tick
    """
    # Convert to m/s
    v1 = v1_vox * (VOXEL_SIZE_M / SECONDS_PER_TICK)
    v2 = v2_vox * (VOXEL_SIZE_M / SECONDS_PER_TICK)

    v_final = (m1 * v1 + m2 * v2) / (m1 + m2)

    # Convert back to voxels/tick
    return v_final * (SECONDS_PER_TICK / VOXEL_SIZE_M)

__all__ = [
    "elastic_collision_1d",
    "inelastic_collision_1d",
]

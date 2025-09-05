"""
Matter properties in voxel space.
"""

from .constants import VOXEL_SIZE_M, VOXELS_PER_M


# --- Volume / voxel conversions ---

def volume_voxels(cubic_m: float) -> int:
    """
    Convert cubic meters to number of voxels³.
    """
    return int(round(cubic_m / (VOXEL_SIZE_M ** 3)))


def volume_m3_from_voxels(voxel_count: int) -> float:
    """
    Convert voxel³ count back to cubic meters.
    """
    return voxel_count * (VOXEL_SIZE_M ** 3)


# --- Mass / density relations ---

def mass_from_density(density_kg_m3: float, volume_m3: float) -> float:
    """
    Mass = density × volume (kg).
    """
    return density_kg_m3 * volume_m3


def density_from_mass(mass_kg: float, volume_m3: float) -> float:
    """
    Density = mass / volume (kg/m³).
    """
    if volume_m3 == 0:
        raise ValueError("Volume cannot be zero")
    return mass_kg / volume_m3


def mass_from_voxels(density_kg_m3: float, voxel_count: int) -> float:
    """
    Mass (kg) given density (kg/m³) and voxel count.
    """
    volume_m3 = volume_m3_from_voxels(voxel_count)
    return density_kg_m3 * volume_m3


def voxels_from_mass(mass_kg: float, density_kg_m3: float) -> int:
    """
    Voxel³ count given mass (kg) and density (kg/m³).
    """
    if density_kg_m3 == 0:
        raise ValueError("Density cannot be zero")
    volume_m3 = mass_kg / density_kg_m3
    return volume_voxels(volume_m3)


# --- Shape helpers (very basic primitives) ---

def cube_voxels(edge_length_m: float) -> int:
    """
    Voxel³ count for a cube of edge length in meters.
    """
    volume_m3 = edge_length_m ** 3
    return volume_voxels(volume_m3)


def sphere_voxels(radius_m: float) -> int:
    """
    Voxel³ count for a sphere of given radius in meters.
    """
    import math
    volume_m3 = (4/3) * math.pi * (radius_m ** 3)
    return volume_voxels(volume_m3)


__all__ = [
    "volume_voxels",
    "volume_m3_from_voxels",
    "mass_from_density",
    "density_from_mass",
    "mass_from_voxels",
    "voxels_from_mass",
    "cube_voxels",
    "sphere_voxels",
]
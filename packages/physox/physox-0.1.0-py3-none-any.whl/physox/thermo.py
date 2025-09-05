"""
Thermodynamics utilities in voxel space.
"""

from .constants import VOXEL_SIZE_M

# --- Pressure ---

def pressure(force_N: float, area_m2: float) -> float:
    """
    Compute pressure in Pascals (N/m²).
    """
    return force_N / area_m2


def pressure_from_depth(density_kg_m3: float, depth_m: float, g: float = 9.80665) -> float:
    """
    Hydrostatic pressure from a fluid column.
    
    Args:
        density_kg_m3: fluid density (kg/m³)
        depth_m: depth of fluid column (m)
        g: gravitational acceleration (m/s²), default = Earth
    
    Returns:
        Pressure (Pa)
    """
    return density_kg_m3 * g * depth_m


# --- Ideal gas law ---

def ideal_gas_pressure(n_moles: float, volume_m3: float, temperature_K: float) -> float:
    """
    Compute pressure using the ideal gas law: P = nRT / V.
    """
    R = 8.314  # J/(mol·K)
    return (n_moles * R * temperature_K) / volume_m3


def ideal_gas_temperature(pressure_Pa: float, volume_m3: float, n_moles: float) -> float:
    """
    Solve ideal gas law for T.
    """
    R = 8.314
    return (pressure_Pa * volume_m3) / (n_moles * R)


def ideal_gas_volume(n_moles: float, temperature_K: float, pressure_Pa: float) -> float:
    """
    Solve ideal gas law for V.
    """
    R = 8.314
    return (n_moles * R * temperature_K) / pressure_Pa


# --- Energy related ---

def heat_energy(mass_kg: float, specific_heat_J_per_kgK: float, delta_T: float) -> float:
    """
    Compute heat energy required: Q = mcΔT.
    """
    return mass_kg * specific_heat_J_per_kgK * delta_T


def latent_heat_energy(mass_kg: float, latent_heat_J_per_kg: float) -> float:
    """
    Compute energy required for phase change (fusion, vaporization, etc.).
    """
    return mass_kg * latent_heat_J_per_kg


__all__ = [
    "pressure",
    "pressure_from_depth",
    "ideal_gas_pressure",
    "ideal_gas_temperature",
    "ideal_gas_volume",
    "heat_energy",
    "latent_heat_energy",
]
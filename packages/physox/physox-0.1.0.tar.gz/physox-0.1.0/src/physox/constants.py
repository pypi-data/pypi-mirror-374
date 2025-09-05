"""
PhysOx constants: physical values expressed in voxel (µm) and tick (s) units.
"""

# --- Core scales ---
VOXEL_SIZE_M = 1e-6          # 1 µm in meters (radial voxel size, invariant)
VOXELS_PER_M = 1 / VOXEL_SIZE_M

SECONDS_PER_TICK = 1         # base time tick = 1 second
TICKS_PER_SECOND = 1 / SECONDS_PER_TICK

# --- Fundamental constants ---
C_M_PER_S = 299_792_458      # speed of light in m/s
C_VOXELS_PER_S = int(C_M_PER_S * VOXELS_PER_M)

G_M3_PER_KG_S2 = 6.67430e-11  # gravitational constant (SI)
# Convert to voxel space: vox³ / (kg·s²)
G_VOXELS3_PER_KG_S2 = G_M3_PER_KG_S2 * (VOXELS_PER_M ** 3)

PLANCK_LENGTH_M = 1.616255e-35
PLANCK_LENGTH_VOXELS = PLANCK_LENGTH_M * VOXELS_PER_M

PLANCK_TIME_S = 5.391247e-44
PLANCK_TIME_TICKS = PLANCK_TIME_S / SECONDS_PER_TICK

# --- Particle masses (kg) ---
MASS_PROTON_KG = 1.6726219e-27
MASS_NEUTRON_KG = 1.6749275e-27
MASS_ELECTRON_KG = 9.1093837e-31

# --- Earth/Moon reference radii ---
R_EARTH_M = 6.371e6
R_EARTH_VOXELS = int(R_EARTH_M * VOXELS_PER_M)

R_MOON_M = 1.737e6
R_MOON_VOXELS = int(R_MOON_M * VOXELS_PER_M)

# --- Astronomical Unit ---
AU_M = 149_597_870_700
AU_VOXELS = int(AU_M * VOXELS_PER_M)

# --- Light year ---
LY_M = 9.4607e15
LY_VOXELS = int(LY_M * VOXELS_PER_M)

__all__ = [
    "VOXEL_SIZE_M",
    "VOXELS_PER_M",
    "SECONDS_PER_TICK",
    "TICKS_PER_SECOND",
    "C_M_PER_S",
    "C_VOXELS_PER_S",
    "G_M3_PER_KG_S2",
    "G_VOXELS3_PER_KG_S2",
    "PLANCK_LENGTH_M",
    "PLANCK_LENGTH_VOXELS",
    "PLANCK_TIME_S",
    "PLANCK_TIME_TICKS",
    "MASS_PROTON_KG",
    "MASS_NEUTRON_KG",
    "MASS_ELECTRON_KG",
    "R_EARTH_M",
    "R_EARTH_VOXELS",
    "R_MOON_M",
    "R_MOON_VOXELS",
    "AU_M",
    "AU_VOXELS",
    "LY_M",
    "LY_VOXELS",
]
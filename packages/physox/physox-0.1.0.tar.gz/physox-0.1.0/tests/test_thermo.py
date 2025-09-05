import pytest
from physox.thermo import (
    pressure,
    pressure_from_depth,
    ideal_gas_pressure,
    ideal_gas_temperature,
    ideal_gas_volume,
    heat_energy,
    latent_heat_energy,
)

def test_pressure():
    assert pressure(10, 2) == 5  # 10 N over 2 m²

def test_pressure_from_depth():
    # Water at 1000 kg/m³, depth = 10 m → ~98,066 Pa
    p = pressure_from_depth(1000, 10)
    assert 98_000 < p < 99_000

def test_ideal_gas_pressure_and_inverses():
    n = 1.0
    V = 0.0224  # m³ (molar volume at STP)
    T = 273.15  # K
    P = ideal_gas_pressure(n, V, T)
    assert 100_000 < P < 110_000  # ~1 atm

    # Check inversion with temperature and volume
    T_back = ideal_gas_temperature(P, V, n)
    assert abs(T_back - T) < 1e-6

    V_back = ideal_gas_volume(n, T, P)
    assert abs(V_back - V) < 1e-6

def test_heat_energy():
    # 1 kg water, c=4184 J/kgK, ΔT=10 K → 41,840 J
    q = heat_energy(1, 4184, 10)
    assert 41_000 < q < 42_000

def test_latent_heat_energy():
    # 1 kg water, latent heat of vaporization ~2.26e6 J/kg
    q = latent_heat_energy(1, 2.26e6)
    assert 2.25e6 < q < 2.27e6

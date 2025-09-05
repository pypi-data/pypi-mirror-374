import pytest
from physox.collisions import elastic_collision_1d, inelastic_collision_1d
from physox.constants import VOXEL_SIZE_M, SECONDS_PER_TICK


def test_elastic_collision_equal_masses():
    m1 = m2 = 1.0  # kg
    v1 = 10.0  # voxels/tick
    v2 = -5.0  # voxels/tick

    v1f, v2f = elastic_collision_1d(m1, v1, m2, v2)

    # Swap velocities for equal masses
    assert pytest.approx(v1f, rel=1e-6) == v2
    assert pytest.approx(v2f, rel=1e-6) == v1


def test_elastic_collision_conservation():
    m1, m2 = 2.0, 3.0
    v1, v2 = 8.0, -4.0

    v1f, v2f = elastic_collision_1d(m1, v1, m2, v2)

    # Convert voxels/tick to m/s
    scale = VOXEL_SIZE_M / SECONDS_PER_TICK
    v1_m, v2_m = v1 * scale, v2 * scale
    v1f_m, v2f_m = v1f * scale, v2f * scale

    # Momentum before/after
    p_before = m1 * v1_m + m2 * v2_m
    p_after = m1 * v1f_m + m2 * v2f_m
    assert pytest.approx(p_after, rel=1e-6) == p_before

    # Kinetic energy before/after
    ke_before = 0.5 * m1 * v1_m**2 + 0.5 * m2 * v2_m**2
    ke_after = 0.5 * m1 * v1f_m**2 + 0.5 * m2 * v2f_m**2
    assert pytest.approx(ke_after, rel=1e-6) == ke_before


def test_inelastic_collision_conservation():
    m1, m2 = 2.0, 3.0
    v1, v2 = 8.0, -4.0

    v_final = inelastic_collision_1d(m1, v1, m2, v2)

    # Convert voxels/tick to m/s
    scale = VOXEL_SIZE_M / SECONDS_PER_TICK
    v1_m, v2_m = v1 * scale, v2 * scale
    v_final_m = v_final * scale

    # Momentum before
    p_before = m1 * v1_m + m2 * v2_m
    # After (stuck together)
    p_after = (m1 + m2) * v_final_m

    assert pytest.approx(p_after, rel=1e-6) == p_before

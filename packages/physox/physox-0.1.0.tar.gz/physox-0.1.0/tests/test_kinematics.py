from physox.kinematics import displacement_voxels, velocity_voxels, to_meters

def test_displacement():
    # constant velocity: 10 vox/tick for 10 ticks → 100 vox
    assert displacement_voxels(10, 0, 10) == 100

def test_acceleration():
    # v0=0, a=1 vox/tick², t=4 → s = 0.5 * 1 * 16 = 8 vox
    assert displacement_voxels(0, 1, 4) == 8

def test_velocity():
    # v0=5, a=2, t=3 → v=11 vox/tick
    assert velocity_voxels(5, 2, 3) == 11

def test_to_meters():
    assert to_meters(1_000_000) == 1.0  # 1e6 µm voxels = 1 meter

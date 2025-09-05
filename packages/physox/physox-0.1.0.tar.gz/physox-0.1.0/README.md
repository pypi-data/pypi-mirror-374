# PhysOx

**PhysOx** — A physics framework for voxelized space-time.  
Built to work alongside [UVoxID](https://github.com/JDPlumbing/uvoxid) (universal voxel addressing) and [tDt](https://github.com/JDPlumbing/tdt) (time delta toolkit).

PhysOx provides **general-purpose physics utilities** expressed in terms of discrete voxel space (1 µm³) and ticks (time steps).  
This makes it possible to simulate mechanics, dynamics, and interactions consistently across scales.

---

## ✨ Features

- **Kinematics** — displacement, velocity, conversions between voxels/ticks and meters/seconds.  
- **Dynamics** — forces, acceleration, Newton’s laws in voxel units.  
- **Momentum & Impulse** — linear momentum, collisions, impulse transfer.  
- **Energy** — kinetic, gravitational, thermal, unit conversions (J ↔ eV).  
- **Gravity** — gravitational force, potential, fields.  
- **Electromagnetism** — Coulomb’s law, electric fields, electrostatic potential.  
- **Thermodynamics** — pressure, ideal gas law, energy per voxel.  
- **Waves** — frequency, wavelength, velocity, energy relations.  
- **Rotational Dynamics** — angular velocity, torque, moment of inertia.  
- **Collision Utilities** — elastic/inelastic collision solvers (2D/3D).  

---

## 📦 Installation

```bash
pip install physox
```

---

## 🔍 Example

```python
from physox.kinematics import displacement_voxels, to_meters
from physox.constants import VOXEL_SIZE_M

# Object with initial velocity 10 voxels/tick, accel = 1 voxel/tick², time = 5 ticks
d_vox = displacement_voxels(v0=10, a=1, t_ticks=5)
d_m = to_meters(d_vox)

print(f"Displacement: {d_vox} voxels ({d_m:.6f} m)")
```

Output:
```
Displacement: 62.5 voxels (0.000063 m)
```

---

## 🧪 Testing

Run the test suite with:

```bash
pytest -v
```

All physics modules are covered with unit tests for correctness.

---

## 📖 Roadmap

- Integrate with UVoxID (spatial indexing).  
- Integrate with tDt (time deltas).  
- Add probabilistic/tolerance layer for quantum-scale behavior.  
- GPU/Rust backends for large-scale simulations.  

---

## 📜 License

Apache 2.0 — free to use, modify, and distribute.

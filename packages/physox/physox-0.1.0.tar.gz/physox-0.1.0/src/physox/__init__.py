import importlib

_modules = [
    "constants",
    "dynamics",
    "electromagnetism",
    "energy",
    "gravity",
    "kinematics",
    "matter",
    "momentum",
    "thermo",
    "waves",
    "collisions",
    "probability",
    "rotation",
]

__all__ = []

for m in _modules:
    module = importlib.import_module(f".{m}", package=__name__)
    globals().update({name: getattr(module, name) for name in module.__all__})
    __all__.extend(module.__all__)

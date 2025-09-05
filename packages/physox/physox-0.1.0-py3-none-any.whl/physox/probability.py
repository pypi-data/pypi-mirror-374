"""
Probability resolution engine for Physox.
"""

import random

def resolve_event(base_chance_per_tick: float, ticks: int = 1, sig_chars: int = 38) -> bool:
    """
    Resolve whether an event occurs based on base chance, ticks, and tolerance.

    Args:
        base_chance_per_tick (float): raw probability per tick (0–1).
        ticks (int): number of ticks to accumulate.
        sig_chars (int): tolerance (digits of significance).
                         Lower sig_chars = fuzzier resolution,
                         higher sig_chars = stricter precision.

    Returns:
        bool: True if the event resolves (occurs), False otherwise.
    """
    if base_chance_per_tick <= 0:
        return False
    if base_chance_per_tick >= 1:
        return True

    scale = 10 ** (38 - sig_chars)
    effective_chance = min(1.0, base_chance_per_tick * ticks / scale)

    return random.random() < effective_chance


def cumulative_probability(base_rate: float, trials: int, sig_chars: int = 38) -> float:
    """
    Compute cumulative probability with tolerance.
    Lower sig_chars => fuzzier => higher effective probability.
    """
    # Normalize tolerance effect (38 is max precision)
    tolerance_factor = 38 / sig_chars
    effective_rate = min(1.0, base_rate * tolerance_factor)
    return 1 - (1 - effective_rate) ** trials


__all__ = [
    "resolve_event",
    "cumulative_probability",
]
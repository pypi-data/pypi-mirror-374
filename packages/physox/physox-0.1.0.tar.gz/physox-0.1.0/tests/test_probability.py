import pytest
from physox.probability import resolve_event, cumulative_probability


def test_cumulative_probability_scaling():
    assert cumulative_probability(0.1, 1_000, sig_chars=38) <= 1.0
    assert cumulative_probability(0.1, 1_000_000, sig_chars=38) <= 1.0
    assert cumulative_probability(1.0, 10) == 1.0
    assert cumulative_probability(0.0, 10) == 0.0


def test_resolve_event_deterministic_edges():
    assert resolve_event(0.0, ticks=1000) is False
    assert resolve_event(1.0, ticks=1) is True


def test_resolve_event_probability_runs():
    # Over many runs, should trigger roughly at expected frequency
    trials = 10_000
    count = sum(resolve_event(0.01, ticks=1) for _ in range(trials))
    # 0.01 × 10,000 ≈ 100 expected
    assert 50 < count < 200  # loose bounds


def test_tolerance_effect():
    low_tol = cumulative_probability(0.01, 1000, sig_chars=10)
    high_tol = cumulative_probability(0.01, 1000, sig_chars=38)
    assert low_tol >= high_tol  # lower precision => fuzzier, higher chance

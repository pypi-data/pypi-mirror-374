"""Tests for metrics calculations."""
import pytest
from progressbox.metrics import WelfordAccumulator, EWMA

def test_welford_mean():
    """Test Welford mean calculation."""
    w = WelfordAccumulator()
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    for v in values:
        w.update(v)
    assert abs(w.mean - 3.0) < 0.001

def test_ewma_smoothing():
    """Test EWMA smoothing."""
    ewma = EWMA(alpha=0.5)
    assert ewma.update(10.0) == 10.0
    assert ewma.update(20.0) == 15.0  # 0.5*20 + 0.5*10

# TODO: Add more tests

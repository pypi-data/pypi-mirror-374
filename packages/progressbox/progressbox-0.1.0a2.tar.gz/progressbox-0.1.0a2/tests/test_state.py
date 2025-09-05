"""Tests for state management."""
import pytest
from progressbox.state import ProgressState, TaskInfo

def test_state_initialization():
    """Test state initializes correctly."""
    state = ProgressState(total=100)
    assert state.total == 100
    assert state.completed == 0
    assert len(state.active_tasks) == 0

# TODO: Add more tests

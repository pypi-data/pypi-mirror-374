"""Tests for rendering with golden snapshots."""
import pytest
from progressbox.render.ascii import ASCIIRenderer
from progressbox.state import ProgressState
from progressbox.config import Config

def test_ascii_renderer_empty():
    """Test ASCII renderer with empty state."""
    config = Config(total=10)
    state = ProgressState(total=10)
    renderer = ASCIIRenderer(config)
    output = renderer.render(state, config)
    # TODO: Assert against golden snapshot
    assert output is not None

# TODO: Add golden frame tests

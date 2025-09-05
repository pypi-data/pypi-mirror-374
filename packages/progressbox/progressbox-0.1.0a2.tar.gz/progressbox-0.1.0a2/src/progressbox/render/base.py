"""Base renderer protocol."""
from typing import Protocol
from progressbox.state import ProgressState
from progressbox.config import Config

class Renderer(Protocol):
    """Protocol for all renderers."""

    def render(self, state: ProgressState, config: Config) -> str:
        """Render the progress display."""
        ...

    def start(self) -> None:
        """Initialize renderer."""
        ...

    def close(self) -> None:
        """Cleanup renderer."""
        ...

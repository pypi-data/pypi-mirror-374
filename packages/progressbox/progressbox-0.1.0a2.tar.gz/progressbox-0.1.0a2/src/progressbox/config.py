"""Configuration dataclasses for ProgressBox.

This module provides configuration classes for controlling ProgressBox behavior,
including display settings, performance tuning, and feature toggles.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional, Callable, Dict, Any
import os
import shutil

@dataclass
class Config:
    """Configuration for progress tracking display and behavior.
    
    This class controls all aspects of ProgressBox operation including display
    formatting, performance characteristics, and behavioral features.
    
    Required Parameters:
        total (int): Total number of tasks to be processed. Must be positive.
    
    Display Parameters:
        n_workers (int): Number of parallel workers to display. Default: 6.
            Must be positive integer.
        inner_width (int | Literal["auto"]): Display box width in characters.
            Default: 68. Valid presets: 60, 68, 84, 100. Use "auto" to detect
            terminal width and select nearest preset.
        unicode (bool): Use Unicode box drawing characters. Default: True.
            If False, falls back to ASCII characters.
        renderer (Literal["ascii", "rich", "jupyter", "string"]): Rendering
            backend to use. Default: "ascii".
    
    Performance Parameters:
        refresh_hz (float): Maximum display refresh rate in Hz. Default: 8.0.
            Higher values provide smoother updates but consume more CPU.
        display_interval (float): Minimum time between renders in seconds.
            Default: 0.1 (100ms). Prevents excessive rendering under load.
    
    Feature Parameters:
        show_stage_analysis (bool): Display stage timing analysis table.
            Default: True. Shows average duration and percentage breakdown.
        show_workers (bool): Display active worker tasks. Default: True.
        max_active_rows (int): Maximum number of active task rows to display.
            Default: 12. Prevents display overflow with many workers.
    
    Metrics Parameters:
        ewma_alpha (float): Smoothing factor for ETA calculation (0-1).
            Default: 0.2. Higher values respond faster to changes.
        cache_speed_factor (float): Speed multiplier for cached tasks (0-1).
            Default: 0.8. Assumes cached operations are 80% faster.
    
    Production Parameters:
        prod_safe (bool): Enable conservative mode for production. Default: False.
            Reduces refresh rate and enables additional error handling.
        headless_ok (bool): Allow graceful degradation in headless environments.
            Default: True. Falls back to logging when no TTY available.
        fail_safe (bool): Never raise exceptions that could crash user jobs.
            Default: True. Catches and logs all rendering errors.
    
    Logging Parameters:
        log_interval_s (float): Interval between progress log messages in seconds.
            Default: 30.0. Set to 0 to disable periodic logging.
        snapshot_interval_s (float): Interval between state snapshots in seconds.
            Default: 10.0. Snapshots are JSON records of current state.
    
    Callback Parameters:
        on_snapshot (Optional[Callable[[dict], None]]): Called on each snapshot.
            Receives snapshot data dictionary. Default: None.
        on_complete (Optional[Callable[[dict], None]]): Called on completion.
            Receives final summary dictionary. Default: None.
    
    Example:
        >>> config = Config(total=100, n_workers=4, inner_width="auto")
        >>> config.validate()  # Raises ValueError if invalid
        >>> actual_width = config.get_display_width()
    """

    # Required
    total: int

    # Display
    n_workers: int = 6
    inner_width: int | Literal["auto"] = 68
    unicode: bool = True
    renderer: Literal["ascii", "rich", "jupyter", "string"] = "ascii"

    # Performance
    refresh_hz: float = 8.0
    display_interval: float = 0.1  # 100ms throttle

    # Features
    show_stage_analysis: bool = True
    show_workers: bool = True
    max_active_rows: int = 12

    # Metrics
    ewma_alpha: float = 0.2
    cache_speed_factor: float = 0.8

    # Production
    prod_safe: bool = False
    headless_ok: bool = True
    fail_safe: bool = True
    disable_threading: bool = False  # For tests

    # Logging
    log_interval_s: float = 30.0
    snapshot_interval_s: float = 10.0

    # Optional callbacks
    on_snapshot: Optional[Callable[[dict], None]] = None
    on_complete: Optional[Callable[[dict], None]] = None
    
    # Width presets for terminal display
    _WIDTH_PRESETS: tuple[int, ...] = field(default=(60, 68, 84, 100), init=False, repr=False)
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization.
        
        Raises:
            ValueError: If any configuration value is invalid.
        """
        self.validate()
    
    def validate(self) -> list:
        """Validate all configuration parameters.
        
        Performs comprehensive validation of all parameters to ensure they
        fall within acceptable ranges and combinations.
        
        Returns:
            list: List of validation errors (empty if all valid)
        
        Raises:
            ValueError: If any parameter is invalid.
            TypeError: If any parameter has the wrong type.
        
        Example:
            >>> config = Config(total=-5)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            ValueError: total must be positive, got -5
        """
        errors = []
        # Required parameters
        if not isinstance(self.total, int) or self.total <= 0:
            raise ValueError(f"total must be positive integer, got {self.total}")
        
        # Display parameters
        if not isinstance(self.n_workers, int) or self.n_workers <= 0:
            raise ValueError(f"n_workers must be positive integer, got {self.n_workers}")
        
        if self.inner_width != "auto":
            if not isinstance(self.inner_width, int) or self.inner_width < 40:
                raise ValueError(f"inner_width must be >= 40 or 'auto', got {self.inner_width}")
        
        if self.renderer not in ("ascii", "rich", "jupyter", "string"):
            raise ValueError(f"renderer must be one of ascii/rich/jupyter/string, got {self.renderer}")
        
        # Performance parameters
        if not isinstance(self.refresh_hz, (int, float)) or self.refresh_hz <= 0:
            raise ValueError(f"refresh_hz must be positive number, got {self.refresh_hz}")
        
        if not isinstance(self.display_interval, (int, float)) or self.display_interval < 0:
            raise ValueError(f"display_interval must be non-negative, got {self.display_interval}")
        
        # Feature parameters
        if not isinstance(self.max_active_rows, int) or self.max_active_rows <= 0:
            raise ValueError(f"max_active_rows must be positive integer, got {self.max_active_rows}")
        
        # Metrics parameters
        if not isinstance(self.ewma_alpha, (int, float)) or not (0 < self.ewma_alpha <= 1):
            raise ValueError(f"ewma_alpha must be in range (0, 1], got {self.ewma_alpha}")
        
        if not isinstance(self.cache_speed_factor, (int, float)) or not (0 < self.cache_speed_factor <= 1):
            raise ValueError(f"cache_speed_factor must be in range (0, 1], got {self.cache_speed_factor}")
        
        # Logging parameters
        if not isinstance(self.log_interval_s, (int, float)) or self.log_interval_s < 0:
            raise ValueError(f"log_interval_s must be non-negative, got {self.log_interval_s}")
        
        if not isinstance(self.snapshot_interval_s, (int, float)) or self.snapshot_interval_s < 0:
            raise ValueError(f"snapshot_interval_s must be non-negative, got {self.snapshot_interval_s}")
        
        return errors
    
    def get_display_width(self) -> int:
        """Get the actual display width to use.
        
        If inner_width is "auto", detects terminal width and selects the
        nearest preset. Otherwise returns the configured width.
        
        Returns:
            int: The display width in characters to use.
        
        Example:
            >>> config = Config(total=10, inner_width="auto")
            >>> width = config.get_display_width()
            >>> width in (60, 68, 84, 100)
            True
        """
        if self.inner_width == "auto":
            return self._detect_terminal_width()
        else:
            return self.inner_width
    
    def _detect_terminal_width(self) -> int:
        """Detect terminal width and return nearest preset.
        
        Uses shutil.get_terminal_size() to detect current terminal width,
        then selects the largest preset that fits with some margin.
        
        Returns:
            int: The best-fit preset width (60, 68, 84, or 100).
        
        Note:
            Falls back to 68 characters if terminal detection fails.
        """
        try:
            # Get terminal size with fallback
            terminal_size = shutil.get_terminal_size(fallback=(80, 24))
            available_width = terminal_size.columns
            
            # Account for border chars (4 chars) and some margin (8 chars)
            usable_width = max(available_width - 12, 40)
            
            # Find largest preset that fits
            for width in reversed(self._WIDTH_PRESETS):
                if width <= usable_width:
                    return width
            
            # If even the smallest doesn't fit, use it anyway
            return min(self._WIDTH_PRESETS)
            
        except (OSError, AttributeError):
            # Terminal detection failed, use reasonable default
            return 68
    
    def get_effective_refresh_rate(self) -> float:
        """Get the effective refresh rate accounting for production mode.
        
        In production safe mode, refresh rate is capped at 4 Hz to reduce
        CPU usage in production environments.
        
        Returns:
            float: Effective refresh rate in Hz.
        
        Example:
            >>> config = Config(total=10, refresh_hz=10.0, prod_safe=True)
            >>> config.get_effective_refresh_rate()
            4.0
        """
        if self.prod_safe:
            return min(self.refresh_hz, 4.0)
        else:
            return self.refresh_hz
    
    def get_bar_chars(self) -> 'BarChars':
        """Get appropriate progress bar characters based on unicode setting.
        
        Returns:
            BarChars: Character set for rendering progress bars.
        
        Example:
            >>> config = Config(total=10, unicode=True)
            >>> chars = config.get_bar_chars()
            >>> chars.filled
            '█'
        """
        return BarChars(use_unicode=self.unicode)
    
    def is_headless_environment(self) -> bool:
        """Check if running in a headless environment.
        
        Detects if the current environment has a TTY available for display.
        
        Returns:
            bool: True if running in headless environment.
        
        Note:
            This is a heuristic check and may not be 100% accurate in all
            environments (e.g., some CI systems, containers).
        """
        # Check if stdout is a TTY
        try:
            import sys
            if not sys.stdout.isatty():
                return True
        except (AttributeError, OSError):
            return True
            
        # Check common headless indicators
        headless_vars = ['CI', 'BUILD_ID', 'JENKINS_URL', 'GITHUB_ACTIONS']
        if any(var in os.environ for var in headless_vars):
            return True
            
        # Check DISPLAY variable on Unix-like systems
        if os.name == 'posix' and 'DISPLAY' not in os.environ:
            return True
            
        return False

@dataclass
class BarChars:
    """Configurable progress bar character sets for different display modes.
    
    Provides Unicode and ASCII character sets for rendering progress bars.
    The appropriate set is selected based on terminal capabilities and
    user preferences.
    
    Parameters:
        use_unicode (bool): Whether to use Unicode characters. Default: True.
            If False, falls back to ASCII-safe characters.
        filled (str): Character for completed progress. Default varies by mode.
        current (str): Character for current progress position. Default varies.
        empty (str): Character for remaining progress. Default varies by mode.
    
    Unicode Characters (default):
        filled: '█' (full block)
        current: '▓' (dark shade)
        empty: '░' (light shade)
    
    ASCII Characters (fallback):
        filled: '#' (hash/pound)
        current: '>' (greater than)
        empty: '-' (dash/hyphen)
    
    Example:
        >>> chars = BarChars(use_unicode=True)
        >>> chars.filled
        '█'
        >>> chars = BarChars(use_unicode=False)
        >>> chars.filled
        '#'
    """
    use_unicode: bool = True
    
    # Unicode characters (preferred)
    filled: str = field(init=False)
    current: str = field(init=False)
    empty: str = field(init=False)
    
    # ASCII fallback characters (always available)
    filled_ascii: str = field(init=False)
    current_ascii: str = field(init=False)
    empty_ascii: str = field(init=False)
    
    # Character definitions
    _UNICODE_FILLED: str = field(default='█', init=False, repr=False)
    _UNICODE_CURRENT: str = field(default='▓', init=False, repr=False)
    _UNICODE_EMPTY: str = field(default='░', init=False, repr=False)
    
    _ASCII_FILLED: str = field(default='#', init=False, repr=False)
    _ASCII_CURRENT: str = field(default='>', init=False, repr=False)
    _ASCII_EMPTY: str = field(default='-', init=False, repr=False)
    
    def __post_init__(self) -> None:
        """Set character values based on unicode preference."""
        # Always set ASCII fallback characters
        object.__setattr__(self, 'filled_ascii', self._ASCII_FILLED)
        object.__setattr__(self, 'current_ascii', self._ASCII_CURRENT)
        object.__setattr__(self, 'empty_ascii', self._ASCII_EMPTY)
        
        # Set active characters based on unicode preference
        if self.use_unicode:
            object.__setattr__(self, 'filled', self._UNICODE_FILLED)
            object.__setattr__(self, 'current', self._UNICODE_CURRENT)
            object.__setattr__(self, 'empty', self._UNICODE_EMPTY)
        else:
            object.__setattr__(self, 'filled', self._ASCII_FILLED)
            object.__setattr__(self, 'current', self._ASCII_CURRENT)
            object.__setattr__(self, 'empty', self._ASCII_EMPTY)
    
    def render_bar(self, progress: float, width: int) -> str:
        """Render a progress bar string with the configured characters.
        
        Args:
            progress (float): Progress value from 0.0 to 1.0.
            width (int): Total width of the progress bar in characters.
        
        Returns:
            str: Rendered progress bar string of exactly `width` characters.
        
        Example:
            >>> chars = BarChars(use_unicode=False)
            >>> chars.render_bar(0.4, 10)
            '###>------'
        """
        if width <= 0:
            return ''
        
        # Clamp progress to valid range
        progress = max(0.0, min(1.0, progress))
        
        # Calculate character counts
        filled_chars = int(progress * width)
        
        # Build the bar
        bar = self.filled * filled_chars
        
        # Add current position marker if not at end
        if filled_chars < width and progress > 0:
            bar += self.current
            filled_chars += 1
        
        # Fill remaining with empty chars
        remaining = width - filled_chars
        bar += self.empty * remaining
        
        return bar[:width]  # Ensure exact width


def create_default_config(total: int, **overrides: Any) -> Config:
    """Create a Config instance with sensible defaults.
    
    This convenience function creates a Config with reasonable defaults
    for most use cases, allowing selective override of specific parameters.
    
    Args:
        total (int): Total number of tasks (required).
        **overrides: Any configuration parameters to override.
    
    Returns:
        Config: Configured instance ready for use.
    
    Example:
        >>> config = create_default_config(100, n_workers=8, unicode=False)
        >>> config.total
        100
        >>> config.n_workers
        8
    """
    defaults = {
        'total': total,
        'n_workers': 6,
        'inner_width': 'auto',
        'unicode': True,
        'renderer': 'ascii',
        'refresh_hz': 8.0,
        'display_interval': 0.1,
        'show_stage_analysis': True,
        'show_workers': True,
        'max_active_rows': 12,
        'ewma_alpha': 0.2,
        'cache_speed_factor': 0.8,
        'prod_safe': False,
        'headless_ok': True,
        'fail_safe': True,
        'log_interval_s': 30.0,
        'snapshot_interval_s': 10.0,
    }
    
    # Apply overrides
    defaults.update(overrides)
    
    return Config(**defaults)

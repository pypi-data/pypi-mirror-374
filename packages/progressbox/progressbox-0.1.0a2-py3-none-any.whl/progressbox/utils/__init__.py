"""Utility functions for ProgressBox."""

from .width import (
    get_display_width,
    truncate_to_width,
    align_left,
    align_right,
    align_center,
    pad_multiline,
    wrap_to_width,
    pad_to_width,  # Legacy function
)

from .terminal import (
    get_terminal_width,
    get_terminal_height,
    is_tty,
    is_jupyter,
    supports_color,
    get_color_support,
    is_windows_terminal,
    get_terminal_info,
    clear_cache,
)

from .formatting import (
    format_duration,
    format_percentage,
    format_file_size,
    format_rate,
    build_progress_bar,
    format_eta,
    build_status_line,
    build_full_progress_display,
    format_scientific,
    format_compact_number,
)

__all__ = [
    # Width utilities
    'get_display_width',
    'truncate_to_width',
    'align_left',
    'align_right',
    'align_center',
    'pad_multiline',
    'wrap_to_width',
    'pad_to_width',
    
    # Terminal utilities
    'get_terminal_width',
    'get_terminal_height',
    'is_tty',
    'is_jupyter',
    'supports_color',
    'get_color_support',
    'is_windows_terminal',
    'get_terminal_info',
    'clear_cache',
    
    # Formatting utilities
    'format_duration',
    'format_percentage',
    'format_file_size',
    'format_rate',
    'build_progress_bar',
    'format_eta',
    'build_status_line',
    'build_full_progress_display',
    'format_scientific',
    'format_compact_number',
]

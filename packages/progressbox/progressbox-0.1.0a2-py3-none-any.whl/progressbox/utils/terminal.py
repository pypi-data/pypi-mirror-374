"""Terminal detection and capability utilities."""
import os
import sys
from functools import lru_cache
from typing import Optional, Tuple


@lru_cache(maxsize=1)
def get_terminal_width() -> int:
    """Get terminal width reliably across platforms.
    
    Returns:
        Terminal width in columns, defaults to 80 if cannot be determined
        
    Examples:
        >>> width = get_terminal_width()
        >>> print(f"Terminal is {width} columns wide")
    """
    # Try multiple methods to get terminal width
    
    # Method 1: shutil.get_terminal_size (Python 3.3+)
    try:
        import shutil
        size = shutil.get_terminal_size()
        if size.columns > 0:
            return size.columns
    except (ImportError, OSError):
        pass
    
    # Method 2: os.get_terminal_size (Unix-like systems)
    try:
        size = os.get_terminal_size()
        if size.columns > 0:
            return size.columns
    except (OSError, AttributeError):
        pass
    
    # Method 3: Environment variables
    try:
        columns = os.environ.get('COLUMNS')
        if columns and columns.isdigit():
            width = int(columns)
            if width > 0:
                return width
    except (ValueError, TypeError):
        pass
    
    # Method 4: Windows-specific (if on Windows)
    if sys.platform == "win32":
        try:
            import subprocess
            result = subprocess.run(['mode', 'con'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Columns:' in line:
                        columns_str = line.split('Columns:')[1].strip()
                        if columns_str.isdigit():
                            return int(columns_str)
        except (ImportError, subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Method 5: Unix stty command
    try:
        import subprocess
        result = subprocess.run(['stty', 'size'], capture_output=True, text=True)
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) == 2 and parts[1].isdigit():
                return int(parts[1])
    except (ImportError, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Default fallback
    return 80


@lru_cache(maxsize=1)
def get_terminal_height() -> int:
    """Get terminal height reliably across platforms.
    
    Returns:
        Terminal height in rows, defaults to 24 if cannot be determined
    """
    # Try multiple methods to get terminal height
    
    # Method 1: shutil.get_terminal_size (Python 3.3+)
    try:
        import shutil
        size = shutil.get_terminal_size()
        if size.lines > 0:
            return size.lines
    except (ImportError, OSError):
        pass
    
    # Method 2: os.get_terminal_size (Unix-like systems)
    try:
        size = os.get_terminal_size()
        if size.lines > 0:
            return size.lines
    except (OSError, AttributeError):
        pass
    
    # Method 3: Environment variables
    try:
        lines = os.environ.get('LINES')
        if lines and lines.isdigit():
            height = int(lines)
            if height > 0:
                return height
    except (ValueError, TypeError):
        pass
    
    # Default fallback
    return 24


@lru_cache(maxsize=1)
def is_tty() -> bool:
    """Check if we're running in a TTY (interactive terminal).
    
    Returns:
        True if stdout is connected to a TTY, False otherwise
        
    Examples:
        >>> if is_tty():
        ...     print("Running interactively")
        ... else:
        ...     print("Output is being redirected")
    """
    return sys.stdout.isatty() if hasattr(sys.stdout, 'isatty') else False


@lru_cache(maxsize=1)
def is_jupyter() -> bool:
    """Detect if running in Jupyter notebook/lab environment.
    
    Returns:
        True if running in Jupyter, False otherwise
        
    Examples:
        >>> if is_jupyter():
        ...     print("Using Jupyter-specific formatting")
        ... else:
        ...     print("Using standard terminal formatting")
    """
    # Check for IPython/Jupyter environment
    try:
        # Check if IPython is available and we're in an interactive session
        import IPython
        if IPython.get_ipython() is not None:
            return True
    except ImportError:
        pass
    
    # Check environment variables set by Jupyter
    jupyter_vars = [
        'JUPYTER_RUNTIME_DIR',
        'JPY_SESSION_NAME',
        'KERNEL_ID',
    ]
    
    for var in jupyter_vars:
        if var in os.environ:
            return True
    
    # Check if we're in a Jupyter kernel
    try:
        import sys
        if 'ipykernel' in sys.modules:
            return True
    except ImportError:
        pass
    
    return False


@lru_cache(maxsize=1)
def supports_color() -> bool:
    """Check if terminal supports ANSI color codes.
    
    Returns:
        True if terminal supports basic ANSI colors, False otherwise
        
    Examples:
        >>> if supports_color():
        ...     print("\\033[31mRed text\\033[0m")
        ... else:
        ...     print("Plain text")
    """
    # If not a TTY, assume no color support
    if not is_tty():
        return False
    
    # Check for explicit color environment variables
    if os.environ.get('NO_COLOR'):
        return False
    
    if os.environ.get('FORCE_COLOR') in ('1', 'true', 'True'):
        return True
    
    # Check TERM environment variable
    term = os.environ.get('TERM', '').lower()
    if not term:
        return False
    
    # Known terminals that support color
    color_terms = [
        'xterm', 'xterm-color', 'xterm-256color',
        'screen', 'screen-256color',
        'tmux', 'tmux-256color',
        'rxvt', 'konsole', 'gnome', 'kitty', 'alacritty'
    ]
    
    for color_term in color_terms:
        if color_term in term:
            return True
    
    # Check for Windows Terminal
    if sys.platform == "win32":
        if os.environ.get('WT_SESSION'):  # Windows Terminal
            return True
        
        # Check Windows version for ANSI support (Windows 10 1607+)
        try:
            import platform
            version = platform.version()
            # Windows 10 build 14393 (1607) and later support ANSI
            if '10.' in version:
                build = int(version.split('.')[-1])
                return build >= 14393
        except (ValueError, ImportError):
            pass
    
    return False


@lru_cache(maxsize=1)
def get_color_support() -> str:
    """Get level of color support available.
    
    Returns:
        Color support level: 'none', 'basic', '256', 'truecolor'
        
    Examples:
        >>> support = get_color_support()
        >>> if support == 'truecolor':
        ...     print("\\033[38;2;255;0;0mTrue color red\\033[0m")
        ... elif support == '256':
        ...     print("\\033[38;5;196m256-color red\\033[0m")
        ... elif support == 'basic':
        ...     print("\\033[31mBasic red\\033[0m")
    """
    if not supports_color():
        return 'none'
    
    # Check for truecolor support
    colorterm = os.environ.get('COLORTERM', '').lower()
    if colorterm in ('truecolor', '24bit'):
        return 'truecolor'
    
    # Check TERM for specific capabilities
    term = os.environ.get('TERM', '').lower()
    
    # Truecolor terminals
    truecolor_terms = ['iterm', 'kitty', 'alacritty', 'wezterm']
    for tc_term in truecolor_terms:
        if tc_term in term:
            return 'truecolor'
    
    # 256-color terminals
    if '256color' in term or '256' in term:
        return '256'
    
    # Windows Terminal supports truecolor
    if sys.platform == "win32" and os.environ.get('WT_SESSION'):
        return 'truecolor'
    
    # Default to basic color support
    return 'basic'


@lru_cache(maxsize=1)
def is_windows_terminal() -> bool:
    """Check if running in Windows Terminal specifically.
    
    Returns:
        True if running in Windows Terminal, False otherwise
    """
    return bool(os.environ.get('WT_SESSION'))


@lru_cache(maxsize=1)
def get_terminal_info() -> dict:
    """Get comprehensive terminal information.
    
    Returns:
        Dictionary with terminal capabilities and properties
        
    Examples:
        >>> info = get_terminal_info()
        >>> print(f"Terminal: {info['width']}x{info['height']}")
        >>> print(f"Color support: {info['color_support']}")
        >>> print(f"TTY: {info['is_tty']}")
    """
    return {
        'width': get_terminal_width(),
        'height': get_terminal_height(),
        'is_tty': is_tty(),
        'is_jupyter': is_jupyter(),
        'supports_color': supports_color(),
        'color_support': get_color_support(),
        'is_windows_terminal': is_windows_terminal(),
        'term': os.environ.get('TERM', ''),
        'colorterm': os.environ.get('COLORTERM', ''),
        'platform': sys.platform,
    }


def clear_cache() -> None:
    """Clear all cached terminal detection results.
    
    Useful when terminal properties might have changed during runtime.
    """
    get_terminal_width.cache_clear()
    get_terminal_height.cache_clear()
    is_tty.cache_clear()
    is_jupyter.cache_clear()
    supports_color.cache_clear()
    get_color_support.cache_clear()
    is_windows_terminal.cache_clear()
    get_terminal_info.cache_clear()
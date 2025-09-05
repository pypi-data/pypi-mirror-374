"""ASCII box renderer with fixed-width display."""
from __future__ import annotations
from typing import List, Dict, Any, Union
from progressbox.state import ProgressState
from progressbox.config import Config, BarChars
from progressbox.metrics import format_time
from progressbox.utils.width import pad_to_width

class ASCIIRenderer:
    """Fixed-width box renderer with stage timing."""

    def __init__(self, config: Config):
        self.config = config
        self.bar_chars = config.get_bar_chars()
        self._setup_dimensions()

    def _setup_dimensions(self) -> None:
        """Calculate display dimensions respecting config width."""
        # Use configured width (fallback to a sane default)
        inner = self.config.get_display_width()  # 60/68/84/100
        self.inner_width = inner
        self.box_width = inner + 2
        
        # Allocate columns proportionally to inner width
        # Keep the same ratios as the original 27│26│30 split (~32% / 31% / 37%)
        self.col1_width = max(18, int(inner * 0.32))
        self.col2_width = max(16, int(inner * 0.31))
        self.col3_width = max(16, inner - self.col1_width - self.col2_width - 2)  # -2 for separators
        
        # Bars scale with width
        self.progress_bar_width = max(30, int(inner * 0.7))
        self.stage_bar_width = max(16, int(inner * 0.28))

    def _pad_line(self, content: str, width: int = None) -> str:
        """Pad line to exact width."""
        if width is None:
            width = self.inner_width
        return pad_to_width(content, width)

    def _render_header(self, state: ProgressState) -> List[str]:
        """Render title section with centered text."""
        lines = []
        
        # Top border
        lines.append("╔" + "═" * self.inner_width + "╗")
        
        # Title line - centered
        title = "Progress Monitoring"
        title_line = self._pad_line(title.center(self.inner_width))
        lines.append("║" + title_line + "║")
        
        # Section separator
        lines.append("╠" + "═" * self.inner_width + "╣")
        
        return lines

    def _render_progress_bar(self, completed_or_state, total=None, width=None) -> Union[List[str], str]:
        """Render main progress bar.
        
        Can be called in two ways:
        1. _render_progress_bar(state) -> List[str] for full rendering
        2. _render_progress_bar(completed, total, width) -> str for simple bar
        """
        # Check if called with state object
        if hasattr(completed_or_state, 'get_completion_ratio'):
            # Original implementation with state object
            state = completed_or_state
            lines = []
            
            # Progress info line
            progress_ratio = state.get_completion_ratio()
            progress_pct = int(progress_ratio * 100)
            
            remaining = state.get_remaining_count()
            active = state.get_active_count()
            
            info_line = f"Tasks: {state.completed}/{state.total} ({progress_pct}%) │ Active: {active} │ Remaining: {remaining}"
            lines.append("║" + self._pad_line(info_line) + "║")
            
            # Progress bar line
            bar = self.bar_chars.render_bar(progress_ratio, self.progress_bar_width)
            bar_line = f"Progress [{bar}] {progress_pct}%"
            lines.append("║" + self._pad_line(bar_line) + "║")
            
            return lines
        else:
            # Simple bar rendering (for tests)
            completed = completed_or_state
            if total is None or width is None:
                raise ValueError("When called with completed count, must provide total and width")
            
            progress_ratio = completed / total if total > 0 else 0.0
            return self.bar_chars.render_bar(progress_ratio, width)

    def _render_stats_table(self, state: ProgressState) -> List[str]:
        """Render 3-column stats rows."""
        lines = []
        
        # Table header separator
        lines.append("╟" + "─" * self.col1_width + "┬" + "─" * self.col2_width + "┬" + "─" * self.col3_width + "╢")
        
        # Header row
        header_line = f"{'Metric':<{self.col1_width}}│{'Value':<{self.col2_width}}│{'Details':<{self.col3_width}}"
        lines.append("║" + header_line + "║")
        
        # Separator
        lines.append("╟" + "─" * self.col1_width + "┼" + "─" * self.col2_width + "┼" + "─" * self.col3_width + "╢")
        
        # Elapsed time
        elapsed = state.get_elapsed_time()
        elapsed_str = format_time(elapsed)
        row1 = f"{'Elapsed Time':<{self.col1_width}}│{elapsed_str:<{self.col2_width}}│{'Total runtime':<{self.col3_width}}"
        lines.append("║" + row1 + "║")
        
        # Average completion time
        avg_time = state.get_average_completion_time()
        avg_str = format_time(avg_time) if avg_time else "N/A"
        row2 = f"{'Avg Task Time':<{self.col1_width}}│{avg_str:<{self.col2_width}}│{'Per task average':<{self.col3_width}}"
        lines.append("║" + row2 + "║")
        
        # Cache statistics
        cache_pct = int((state.cached_loads / max(state.completed, 1)) * 100) if state.completed > 0 else 0
        row3 = f"{'Cached Tasks':<{self.col1_width}}│{f'{state.cached_loads} ({cache_pct}%)':<{self.col2_width}}│{'Using cached results':<{self.col3_width}}"
        lines.append("║" + row3 + "║")
        
        return lines

    def _render_stage_analysis(self, state: ProgressState) -> List[str]:
        """Render stage timing with percentages."""
        lines = []
        
        stage_stats = state.get_stage_statistics()
        if not stage_stats:
            return lines
        
        # Section separator
        lines.append("╠" + "═" * self.inner_width + "╣")
        
        # Section title
        title_line = self._pad_line("Stage Analysis".center(self.inner_width))
        lines.append("║" + title_line + "║")
        
        # Table header
        lines.append("╟" + "─" * self.col1_width + "┬" + "─" * self.col2_width + "┬" + "─" * self.col3_width + "╢")
        header = f"{'Stage':<{self.col1_width}}│{'Avg Time':<{self.col2_width}}│{'Progress':<{self.col3_width}}"
        lines.append("║" + header + "║")
        lines.append("╟" + "─" * self.col1_width + "┼" + "─" * self.col2_width + "┼" + "─" * self.col3_width + "╢")
        
        # Stage rows with progress bars
        for stage, stats in sorted(stage_stats.items()):
            avg_time_str = format_time(stats['mean'])
            pct = int(stats['percentage'])
            
            # Create mini progress bar for this stage
            stage_progress = min(1.0, stats['percentage'] / 100)
            mini_bar = self._get_stage_progress(stage, stage_progress)
            
            row = f"{stage[:self.col1_width-1]:<{self.col1_width}}│{avg_time_str:<{self.col2_width}}│{mini_bar:<{self.col3_width}}"
            lines.append("║" + row + "║")
        
        return lines

    def _render_active_tasks(self, state: ProgressState, config: Config) -> List[str]:
        """Render worker status with mini progress bars."""
        lines = []
        
        active_tasks = state.get_active_tasks()
        if not active_tasks:
            return lines
        
        # Section separator
        lines.append("╠" + "═" * self.inner_width + "╣")
        
        # Section title
        title_line = self._pad_line("Active Workers".center(self.inner_width))
        lines.append("║" + title_line + "║")
        
        # Table header
        lines.append("╟" + "─" * self.col1_width + "┬" + "─" * self.col2_width + "┬" + "─" * self.col3_width + "╢")
        header = f"{'Worker':<{self.col1_width}}│{'Stage':<{self.col2_width}}│{'Duration':<{self.col3_width}}"
        lines.append("║" + header + "║")
        lines.append("╟" + "─" * self.col1_width + "┼" + "─" * self.col2_width + "┼" + "─" * self.col3_width + "╢")
        
        # Limit to max_active_rows
        displayed_tasks = active_tasks[:config.max_active_rows]
        
        for task in displayed_tasks:
            worker_id = f"Worker {task.worker_id}"
            stage = task.stage[:self.col2_width-1]  # Truncate if needed
            duration_str = format_time(task.get_task_duration())
            
            row = f"{worker_id:<{self.col1_width}}│{stage:<{self.col2_width}}│{duration_str:<{self.col3_width}}"
            lines.append("║" + row + "║")
        
        # Show "and X more" if we truncated
        if len(active_tasks) > config.max_active_rows:
            remaining_count = len(active_tasks) - config.max_active_rows
            more_line = f"... and {remaining_count} more workers"
            lines.append("║" + self._pad_line(more_line.center(self.inner_width)) + "║")
        
        return lines

    def _get_stage_progress(self, stage: str, progress: float) -> str:
        """Generate 24-char progress bar for stage."""
        bar = self.bar_chars.render_bar(progress, self.stage_bar_width - 6)  # Leave space for percentage
        pct = int(progress * 100)
        return f"[{bar}] {pct:2d}%"

    def render(self, state: ProgressState, config: Config) -> str:
        """Render the complete box matching VLF pattern."""
        lines = []
        
        # Render all sections
        lines.extend(self._render_header(state))
        lines.extend(self._render_progress_bar(state))
        lines.extend(self._render_stats_table(state))
        
        if config.show_stage_analysis:
            lines.extend(self._render_stage_analysis(state))
        
        if config.show_workers:
            lines.extend(self._render_active_tasks(state, config))
        
        # Bottom border
        lines.append("╚" + "═" * self.inner_width + "╝")
        
        return "\n".join(lines)

    def start(self) -> None:
        """Initialize renderer."""
        pass

    def close(self) -> None:
        """Cleanup renderer."""
        pass

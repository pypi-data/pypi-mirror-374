"""Event types for IPC communication."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional, Hashable, Dict, Any, Tuple
import time

@dataclass
class ProgressEvent:
    """IPC event for worker→main communication."""
    type: Literal["start", "update", "finish", "done", "error"]
    task_id: Hashable
    timestamp: float = field(default_factory=time.time)

    # Optional fields
    worker_id: Optional[int] = None
    stage: Optional[str] = None
    progress: Optional[float] = None  # 0.0-1.0
    sub_progress: Optional[Tuple[int, int]] = None  # (current, total)
    cached: bool = False
    meta: Optional[Dict[str, Any]] = None
    error_msg: Optional[str] = None

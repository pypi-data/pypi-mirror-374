"""
ProgressBox - Stage-aware progress monitoring for parallel Python jobs
"""
from progressbox.core import Progress
from progressbox.config import Config

__version__ = "0.1.0a1"
__all__ = ["Progress", "Config", "Reporter", "consume", "Manager"]

def __getattr__(name):
    if name in {"Reporter", "consume", "Manager"}:
        # Lazy import to avoid side-effects when only Progress/Config are needed
        from importlib import import_module
        if name == "Reporter":
            return import_module("progressbox.ipc.reporter").Reporter
        if name == "consume":
            return import_module("progressbox.ipc.queue").consume
        if name == "Manager":
            return import_module("progressbox.ipc.manager").Manager
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

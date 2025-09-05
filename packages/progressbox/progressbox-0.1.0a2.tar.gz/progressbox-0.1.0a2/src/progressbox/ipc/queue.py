"""Queue-based IPC consumer for main process."""
from __future__ import annotations
from multiprocessing import Queue
from typing import Optional, Dict, Any
import time
import queue as queue_module
from progressbox.core import Progress
from progressbox.events import ProgressEvent

def consume(
    queue: Queue,
    progress: Progress,
    refresh_hz: float = 8.0,
    *,
    manage_progress: bool = True
) -> None:
    """
    Consumer loop for main process.
    Reads events from queue and updates progress display.
    
    This function implements an event coalescing algorithm to handle
    high-volume event streams efficiently. It batches updates per task_id
    and renders at a controlled refresh rate.
    
    Args:
        queue (Queue): Multiprocessing queue to read events from.
        progress (Progress): Progress instance to update with events.
        refresh_hz (float): Target refresh rate in Hz. Default: 8.0.
        manage_progress (bool): Whether to call start()/close() on progress. Default: True.
        
    Algorithm:
        1. Read events with timeout (non-blocking)
        2. Coalesce updates per task_id (keep latest)
        3. Render display at refresh_hz intervals
        4. Process "done" event to exit cleanly
    """
    frame_interval = 1.0 / refresh_hz  # Time between frames
    next_frame = time.time() + frame_interval
    coalesced: Dict[Any, ProgressEvent] = {}  # task_id -> latest update
    running = True
    timeout = min(0.1, frame_interval * 0.5)  # Cap timeout at 100ms for responsiveness
    
    # Start the progress display if requested
    if manage_progress:
        try:
            progress.start()
        except Exception as e:
            print(f"Warning: Failed to start progress display: {e}")
            manage_progress = False  # Don't try to close if start failed
    
    try:
        while running:
            current_time = time.time()
            
            # Read events until timeout or no more events
            events_processed = 0
            event_loop_running = True
            while event_loop_running and running:
                try:
                    # Use short timeout for responsiveness
                    event: ProgressEvent = queue.get(timeout=timeout)
                    events_processed += 1
                    
                    # Handle different event types
                    if event.type == "done":
                        # Process any remaining coalesced events
                        _apply_coalesced_events(coalesced, progress)
                        coalesced.clear()
                        running = False
                        break
                    elif event.type in ("start", "finish", "error"):
                        # Process any pending updates for this task first
                        if event.task_id in coalesced:
                            pending_update = coalesced.pop(event.task_id)
                            if event.type == "start":
                                # Apply start first, then update
                                _process_immediate_event(event, progress)
                                _apply_single_event(pending_update, progress)
                            else:
                                # Apply update first, then finish/error
                                _apply_single_event(pending_update, progress)
                                _process_immediate_event(event, progress)
                        else:
                            # No pending update, process immediately
                            _process_immediate_event(event, progress)
                    elif event.type == "update":
                        # Updates are coalesced per task_id
                        if event.task_id is not None:
                            coalesced[event.task_id] = event
                    
                    current_time = time.time()
                    
                    # Limit event processing per frame to prevent blocking
                    if events_processed >= 100:  # Process max 100 events per batch
                        event_loop_running = False
                        
                except queue_module.Empty:
                    # No more events available, break to check for frame update
                    event_loop_running = False
                except Exception as e:
                    # Log error but continue processing
                    print(f"Error processing event: {e}")
                    continue
            
            # Check if it's time for a frame update
            current_time = time.time()
            if current_time >= next_frame:
                # Apply coalesced events and render
                if coalesced:
                    _apply_coalesced_events(coalesced, progress)
                    coalesced.clear()
                
                # Schedule next frame
                next_frame = current_time + frame_interval
                
                # Small sleep to prevent excessive CPU usage
                time.sleep(0.001)
    
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        running = False
    except Exception as e:
        # Handle any other errors but continue to cleanup
        print(f"Consumer error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ensure progress display is properly closed
        if manage_progress:
            try:
                progress.close()
            except Exception as e:
                print(f"Warning: Failed to close progress display: {e}")

def _process_immediate_event(event: ProgressEvent, progress: Progress) -> None:
    """Process events that need immediate handling (start, finish, error).
    
    Args:
        event (ProgressEvent): Event to process.
        progress (Progress): Progress instance to update.
    """
    try:
        if event.type == "start":
            progress.task_start(
                task_id=event.task_id,
                worker=event.worker_id,
                cached=event.cached,
                meta=event.meta
            )
        elif event.type == "finish":
            progress.task_finish(event.task_id)
        elif event.type == "error":
            # For now, treat errors as task finish
            # In the future, could add error handling to Progress class
            progress.task_finish(event.task_id)
    except Exception as e:
        # Don't let individual event processing errors crash the consumer
        print(f"Error processing {event.type} event for task {event.task_id}: {e}")

def _apply_single_event(event: ProgressEvent, progress: Progress) -> None:
    """Apply a single update event to the progress tracker.
    
    Args:
        event (ProgressEvent): Update event to apply.
        progress (Progress): Progress instance to update.
    """
    try:
        progress.task_update(
            task_id=event.task_id,
            stage=event.stage,
            progress=event.progress,
            sub_progress=event.sub_progress
        )
    except Exception as e:
        # Don't let individual event processing errors crash the consumer
        print(f"Error applying update for task {event.task_id}: {e}")

def _apply_coalesced_events(coalesced: Dict[Any, ProgressEvent], progress: Progress) -> None:
    """Apply all coalesced update events to the progress tracker.
    
    Args:
        coalesced (Dict[Any, ProgressEvent]): Map of task_id to latest update event.
        progress (Progress): Progress instance to update.
    """
    for task_id, event in coalesced.items():
        _apply_single_event(event, progress)

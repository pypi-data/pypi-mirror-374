# ProgressBox 📦

> Stage-aware progress monitoring for parallel Python jobs

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

## Features

- 🎯 **Stage-aware tracking** - Monitor different stages of computation with timing analysis
- ⚡ **True parallelism** - Built for multiprocessing, threading, and joblib
- 📊 **Rich statistics** - ETA, throughput, stage timing breakdown
- 🖼️ **Beautiful display** - Fixed-width Unicode box with perfect alignment
- 🔧 **Production ready** - Logging, snapshots, error handling

## Installation

```bash
pip install progressbox
```

## Quick Start

```python
import progressbox as pbox

# Simple usage
config = pbox.Config(total=100, n_workers=4)
with pbox.Progress(config) as progress:
    for i in range(100):
        progress.task_start(i, worker=i % 4)
        progress.task_update(i, stage="processing")
        # ... do work ...
        progress.task_finish(i)
```

## Joblib Integration

```python
from joblib import Parallel, delayed
import progressbox as pbox

# Your existing joblib code, now with progress!
results = pbox.adapters.joblib_progress(
    items,
    process_func,
    n_jobs=6,
    config=pbox.Config(total=len(items))
)
```

## Documentation

See [full documentation](https://progressbox.readthedocs.io) for more examples and API reference.

## License

MIT License - see LICENSE file for details.

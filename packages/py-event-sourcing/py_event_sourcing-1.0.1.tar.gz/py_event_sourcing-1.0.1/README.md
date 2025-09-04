# py-event-sourcing - A minimal, `asyncio`-native event sourcing library

[![CI](https://github.com/johnlogsdon/py-event-sourcing/actions/workflows/ci.yml/badge.svg)](https://github.com/johnlogsdon/py-event-sourcing/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/py-event-sourcing.svg)](https://pypi.org/project/py-event-sourcing/)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-event-sourcing)](https://pypi.org/project/py-event-sourcing/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This library provides core components for building event-sourced systems in Python. It uses SQLite for persistence and offers a simple API for `write`, `read`, and `watch` operations on event streams.

For a deeper dive into the concepts and design, please see:
*   **[Concepts](docs/CONCEPTS.md)**: An introduction to the Event Sourcing pattern.
*   **[Design](docs/DESIGN.md)**: An overview of the library's architecture and components.

## Key Features

*   **Simple & Serverless**: Uses SQLite for a file-based, zero-dependency persistence layer.
*   **Global Event Stream**: Query all events across all streams in their global sequence using the special `'@all'` stream, perfect for building cross-stream read models or for auditing.
*   **Idempotent Writes**: Prevents duplicate events in distributed systems by using an optional `id` on each event.
*   **Optimistic Concurrency Control**: Ensures data integrity by allowing writes only against a specific, expected stream version.
*   **Efficient Watching**: A centralized notifier polls the database once to serve all watchers, avoiding the "thundering herd" problem and ensuring low-latency updates.
*   **Snapshot Support**: Accelerate state reconstruction for long-lived streams by saving and loading state snapshots. This is also supported for the `'@all'` stream, which is ideal for complex, system-wide projections.
*   **Fully Async API**: Built from the ground up with `asyncio` for high-performance, non-blocking I/O.
*   **Extensible by Design**: Core logic is decoupled from storage implementation via `Protocol`-based adapters. While this package provides a highly-optimized SQLite backend, you can easily create your own adapters for other databases (e.g., PostgreSQL, Firestore).

## Installation

This project uses `uv` for dependency management.

1.  **Create and activate the virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

2.  **Install the package in editable mode with dev dependencies:**
    ```bash
    uv pip install -e ".[dev]"
    ```

## Quick Start

Here’s a quick example of writing to and reading from a stream.

```python
import asyncio
import os
import tempfile
from py_event_sourcing import sqlite_stream_factory, CandidateEvent

async def main():
    # Use a temporary file for the database to keep the example self-contained.
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "example.db")

        # The factory is an async context manager that handles all resources.
        async with sqlite_stream_factory(db_path) as open_stream:
            stream_id = "my_first_stream"

            # Write an event
            async with open_stream(stream_id) as stream:
                event = CandidateEvent(type="UserRegistered", data=b'{"user": "Alice"}')
                await stream.write([event])
                print(f"Event written. Stream version is now {stream.version}.")

            # Read the event back
            async with open_stream(stream_id) as stream:
                all_events = [e async for e in stream.read()]
                print(f"Read {len(all_events)} event(s) from the stream.")
                print(f"  -> Event type: {all_events[0].type}, Data: {all_events[0].data.decode()}, Version: {all_events[0].version}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Basic Usage

For a detailed, fully-commented example covering all major features (writing, reading, snapshots, and watching), please see [`basic_usage.py`](basic_usage.py).

To run the example:
```bash
uv run python3 basic_usage.py
```

**Sample Output:**
```
--- Example 1: Writing and Reading Events ---
Stream 'counter_stream_1' is now at version 3.
Reading all events from the stream:
  - Event version 1: Increment
  - Event version 2: Increment
  - Event version 3: Decrement

--- Example 2: Reconstructing State from Events (Read Model & Projector) ---
Reconstructed state: Counter is 1.

--- Example 3: Watching for New Events ---
Watching for events (historical and new)...
  - Watched event: Increment (version 1)
  - Watched event: Increment (version 2)
  - Watched event: Decrement (version 3)
Writing new events to trigger the watcher...
  - Watched event: Increment (version 4)
  - Watched event: Increment (version 5)

--- Example 4: Using Snapshots for Efficiency ---
Snapshot for 'counter' projection saved at version 5 with state: count = 3
State for 'counter' projection restored from snapshot at version 5. Count is 3.
Replaying events since snapshot...
  - Applying event version 6: Increment
Final reconstructed state: Counter is 4.
```

## Benchmarks

A benchmark script is included to measure write/read throughput and demonstrate the performance benefits of using snapshots. You can find the script at [`benchmark.py`](benchmark.py).

To run the benchmark:
```bash
uv run python3 benchmark.py
```

**Sample Output:**
```
--- Running benchmark with 1,000,000 events ---
Writing 1,000,000 events...

Finished writing 1,000,000 events in 9.41 seconds.
Write throughput: 106,320.88 events/sec.

--- Benchmark 1: Reconstructing state from all events ---
Reconstructed state (all events): Counter is 1,000,000.
Time to reconstruct from all events: 2.66 seconds.
Read throughput: 375,273.94 events/sec.

--- Benchmark 2: Reconstructing state using snapshot ---
Creating snapshot...
Snapshot created.
Writing 100 additional events...
Finished writing 100 additional events.
State restored from snapshot at version 1,000,000.
Reconstructed state (with snapshot): Counter is 1,000,100.
Time to reconstruct with snapshot: 0.00 seconds.

--- Benchmark Summary ---
Time to reconstruct from all 1,000,100 events: 2.66 seconds.
Time to reconstruct with snapshot (after 1,000,000 events): 0.0007 seconds.

Database file size: 148.13 MB
```

## Testing

The test suite uses `pytest`. To run all tests, use the following command:

```bash
uv run pytest
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up a development environment
- Code style guidelines
- Testing requirements
- Pull request process

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
# Substrate telemetry client

A Python client for [Substrate's telemetry backend](https://github.com/paritytech/substrate-telemetry), providing real-time access to node data from chains like Polkadot and Kusama. It offers both synchronous and asynchronous interfaces.

## Quick start

1.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install the package in editable mode:**
    ```bash
    pip install -e .
    ```

3.  **Run the example script:**
    ```bash
    python3 examples/basic_usage.py
    ```

## Usage

This client can be used in two ways: synchronously or asynchronously.

### `TelemetryClient`

The `TelemetryClient` provides a simple, blocking interface that runs network communication in a background thread.

```python
import time
from substrate_telemetry_client import TelemetryClient, ChainGenesis

with TelemetryClient(chain=ChainGenesis.POLKADOT) as client:
    # Some time for data to arrive
    time.sleep(5)
    nodes = client.get_nodes()

    if nodes:
        print(nodes[0])
```

### `AsyncTelemetryClient`

The `AsyncTelemetryClient` is designed for `asyncio`-based applications.

```python
import asyncio
from substrate_telemetry_client import AsyncTelemetryClient, ChainGenesis

async def main():
    client = AsyncTelemetryClient(chain=ChainGenesis.KUSAMA)
    connect_task = asyncio.create_task(client.connect())
    # ... use client methods ...
    await client.disconnect()
```

For runnable examples demonstrating usage, please see the scripts in the `examples/` directory.

## Data structures

The client returns data in `dataclasses` like `NodeInfo` and `ChainStats`.

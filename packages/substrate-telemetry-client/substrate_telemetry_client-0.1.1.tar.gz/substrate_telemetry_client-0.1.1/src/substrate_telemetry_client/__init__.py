"""
Python client for Substrate telemetry.
"""

__version__ = "0.1.0"

from .async_client import AsyncTelemetryClient
from .client import TelemetryClient
from .constants import ChainGenesis
from .types import (
    BlockInfo,
    ChainStats,
    HardwareInfo,
    IOInfo,
    LocationInfo,
    NetworkInfo,
    NodeInfo,
    Ranking,
    SystemInfo,
)

__all__ = [
    # Clients
    "TelemetryClient",
    "AsyncTelemetryClient",
    "ChainGenesis",

    # Data types
    "NodeInfo",
    "ChainStats",
    "NetworkInfo",
    "SystemInfo",
    "IOInfo",
    "HardwareInfo",
    "BlockInfo",
    "LocationInfo",
    "Ranking",
]

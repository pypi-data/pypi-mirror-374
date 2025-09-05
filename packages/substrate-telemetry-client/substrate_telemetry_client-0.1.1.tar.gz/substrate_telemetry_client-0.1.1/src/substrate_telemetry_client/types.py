from dataclasses import dataclass, field, fields
from typing import Any, List, Optional, Tuple


@dataclass
class NetworkInfo:
    peer_count: int
    peer_id: Optional[str] = None
    ip: Optional[str] = None

@dataclass
class Benchmarks:
    cpu_hashrate_score: Optional[Any] = None
    parallel_cpu_hashrate_score: Optional[Any] = None
    memory_memcpy_score: Optional[Any] = None
    disk_sequential_write_score: Optional[Any] = None
    disk_random_write_score: Optional[Any] = None
    cpu_vendor: Optional[str] = None

@dataclass
class SystemInfo:
    target_os: str
    target_arch: str
    target_env: str
    cpu: Optional[str] = None
    memory: Optional[int] = None
    core_count: Optional[int] = None
    is_virtual_machine: Optional[bool] = None
    linux_kernel: Optional[str] = None
    linux_distro: Optional[str] = None
    benchmarks: Optional[Benchmarks] = None

@dataclass
class IOInfo:
    state_cache_size: List[float] = field(default_factory=list)

@dataclass
class HardwareInfo:
    upload: List[float] = field(default_factory=list)
    download: List[float] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)

@dataclass
class BlockInfo:
    height: int
    hash: str
    propagation_time: Optional[int] = None
    finalized: Optional[int] = None
    finalized_hash: Optional[str] = None

@dataclass
class LocationInfo:
    latitude: float
    longitude: float
    city: str

@dataclass
class NodeInfo:
    id: int
    name: str
    implementation: str
    version: str
    updated_at: str
    validator: Optional[str] = None
    network_info: Optional[NetworkInfo] = None
    system_info: Optional[SystemInfo] = None
    transaction_count: Optional[int] = None
    io: Optional[IOInfo] = None
    hardware: Optional[HardwareInfo] = None
    block: Optional[BlockInfo] = None
    location: Optional[LocationInfo] = None
    startup_time: Optional[int] = None
    stale: bool = False


@dataclass
class Ranking:
    list: List[Tuple[Any, int]]
    other: int
    unknown: int

@dataclass
class ChainStats:
    core_count: Ranking
    cpu: Ranking
    cpu_hashrate_score: Ranking
    parallel_cpu_hashrate_score: Ranking
    cpu_vendor: Ranking
    disk_random_write_score: Ranking
    disk_sequential_write_score: Ranking
    is_virtual_machine: Ranking
    linux_distro: Ranking
    linux_kernel: Ranking
    memory: Ranking
    memory_memcpy_score: Ranking
    target_arch: Ranking
    target_os: Ranking
    version: Ranking

    def __post_init__(self):
        for f in fields(self):
            val = getattr(self, f.name)
            if isinstance(val, dict):
                setattr(self, f.name, Ranking(**val))

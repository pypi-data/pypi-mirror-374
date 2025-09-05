import json
import logging
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Tuple

from .constants import FEED_VERSION, Action
from .exceptions import FeedVersionError
from .types import (
    Benchmarks,
    BlockInfo,
    ChainStats,
    HardwareInfo,
    IOInfo,
    LocationInfo,
    NetworkInfo,
    NodeInfo,
    SystemInfo,
)

logger = logging.getLogger(__name__)

class TelemetryEngine:
    def __init__(self):
        self.nodes: Dict[int, NodeInfo] = {}
        self.chain_stats: Optional[ChainStats] = None
        self._lock = Lock()

    def process_message(self, message: str) -> None:
        try:
            parsed = json.loads(message)
            i = 0
            while i < len(parsed):
                action_id_raw, payload = parsed[i], parsed[i+1]
                try:
                    action_id = Action(action_id_raw)
                    self.handle_action(action_id, payload)
                except ValueError:
                    logger.warning(f"Received unknown action ID: {action_id_raw}")
                i += 2
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
        except FeedVersionError:
            raise
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def handle_action(self, action_id: Action, payload: Any) -> None:
        if action_id == Action.FeedVersion:
            if str(payload) != FEED_VERSION:
                raise FeedVersionError(
                    f"Feed version mismatch: expected {FEED_VERSION}, got {payload}."
                )
        elif action_id == Action.AddedNode:
            self._handle_added_node(payload)
        elif action_id == Action.RemovedNode:
            with self._lock:
                self.nodes.pop(payload, None)
        elif action_id == Action.ChainStatsUpdate:
            with self._lock:
                self.chain_stats = ChainStats(**payload)
        elif action_id in (
            Action.NodeStatsUpdate, Action.Hardware, Action.ImportedBlock,
            Action.FinalizedBlock, Action.LocatedNode, Action.NodeIOUpdate,
            Action.StaleNode
        ):
            self._update_node(action_id, payload)

    def _handle_added_node(self, payload: List[Any]) -> None:
        node_id, details, stats, io, hw, block, loc, startup = payload
        name, impl, ver, val, net_id, os, arch, env, ip, sys_raw, bench_raw = details

        benchmarks = None
        if bench_raw is not None:
            benchmarks = Benchmarks(**bench_raw)

        system_info = None
        if sys_raw is not None:
            system_info = SystemInfo(
                target_os=os, target_arch=arch, target_env=env,
                benchmarks=benchmarks,
                **sys_raw
            )

        node = NodeInfo(
            id=node_id, name=name, implementation=impl, version=ver,
            validator=val or None,
            network_info=NetworkInfo(
                peer_count=stats[0], peer_id=net_id or None, ip=ip or None
            ),
            system_info=system_info,
            transaction_count=stats[1],
            io=IOInfo(state_cache_size=io[0]) if io else None,
            hardware=HardwareInfo(
                upload=hw[0], download=hw[1], timestamps=hw[2]
            ) if hw else None,
            block=BlockInfo(
                height=block[0], hash=block[1], propagation_time=block[4] or None
            ) if block else None,
            location=LocationInfo(
                latitude=loc[0], longitude=loc[1], city=loc[2]
            ) if loc else None,
            startup_time=startup,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self.nodes[node_id] = node

    def _update_node(self, action_id: Action, payload: Any) -> None:
        with self._lock:
            node_id = payload if action_id == Action.StaleNode else payload[0]
            node = self.nodes.get(node_id)
            if not node:
                return

            updater, data = self._get_updater_and_data(action_id, payload)
            if updater:
                updater(node, data)
            node.updated_at = datetime.now(timezone.utc).isoformat()

    def _get_updater_and_data(
        self, action_id: Action, payload: Any
    ) -> Tuple[Optional[Callable], Any]:
        updaters = {
            Action.NodeStatsUpdate: (self._update_stats, payload[1]),
            Action.Hardware: (self._update_hardware, payload[1]),
            Action.ImportedBlock: (self._update_imported_block, payload[1]),
            Action.FinalizedBlock: (self._update_finalized_block, payload[1:]),
            Action.LocatedNode: (self._update_location, payload[1:]),
            Action.NodeIOUpdate: (self._update_io, payload[1]),
            Action.StaleNode: (self._mark_stale, None),
        }
        return updaters.get(action_id, (None, None))

    def _update_stats(self, node: NodeInfo, data: Any):
        peers, txs = data
        if node.network_info:
            node.network_info.peer_count = peers
        node.transaction_count = txs

    def _update_hardware(self, node: NodeInfo, data: Any):
        if not node.hardware:
            node.hardware = HardwareInfo()
        node.hardware.upload, node.hardware.download, node.hardware.timestamps = data

    def _update_imported_block(self, node: NodeInfo, data: Any):
        height, hash, _, _, prop_time = data
        if not node.block:
            node.block = BlockInfo(height=height, hash=hash)
        node.block.height = height
        node.block.hash = hash
        node.block.propagation_time = prop_time or None

    def _update_finalized_block(self, node: NodeInfo, data: Any):
        height, hash = data
        if node.block:
            node.block.finalized = height
            node.block.finalized_hash = hash

    def _update_location(self, node: NodeInfo, data: Any):
        lat, lon, city = data
        node.location = LocationInfo(latitude=lat, longitude=lon, city=city)

    def _update_io(self, node: NodeInfo, data: Any):
        if not node.io:
            node.io = IOInfo()
        node.io.state_cache_size = data[0]

    def _mark_stale(self, node: NodeInfo, data: Any):
        node.stale = True

    def get_nodes(self) -> List[NodeInfo]:
        with self._lock:
            return list(self.nodes.values())

    def get_node(self, node_id: int) -> Optional[NodeInfo]:
        with self._lock:
            return self.nodes.get(node_id)

    def get_chain_stats(self) -> Optional[ChainStats]:
        with self._lock:
            return self.chain_stats

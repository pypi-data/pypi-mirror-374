import asyncio
import logging
import threading
from concurrent.futures import Future
from typing import List, Optional

from .async_client import AsyncTelemetryClient
from .types import ChainStats, NodeInfo

logger = logging.getLogger(__name__)

class TelemetryClient:
    def __init__(self, *args, **kwargs):
        self._client = AsyncTelemetryClient(*args, **kwargs)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._connect_future: Optional[Future] = None

    @property
    def is_running(self) -> bool:
        return self._client.is_running

    def connect(self):
        """
        Starts the background event loop and connects to the telemetry service.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # An expected case when no loop is running
            pass
        else:
            raise RuntimeError(
                "The synchronous TelemetryClient cannot be used from within an "
                "active asyncio event loop. Use the AsyncTelemetryClient instead."
            )

        if self._thread.is_alive():
            return

        self._thread.start()
        self._connect_future = asyncio.run_coroutine_threadsafe(
            self._client.connect(), self._loop
        )
        self._connect_future.add_done_callback(self._log_connect_exception)

    def _log_connect_exception(self, future: Future):
        if future.cancelled():
            return
        if exception := future.exception():
            logger.error(f"The background connection task failed: {exception}")

    def disconnect(self):
        if not self._thread.is_alive() or not self._client.is_running:
            return

        # Ask the client to teardown its WebSocket
        future = asyncio.run_coroutine_threadsafe(self._client.disconnect(), self._loop)
        try:
            future.result(timeout=10)
        except Exception as e:
            logger.warning("Error in async client.disconnect(): %r", e)

        # Cancel (and wait on) the connect loop
        if self._connect_future:
            self._connect_future.cancel()
            try:
                self._connect_future.result(timeout=10)
            except Exception:
                logger.debug("Connect future did not shut down cleanly.")

        # Cancel any other pending tasks
        def _cancel_all():
            for t in asyncio.all_tasks():
                if not t.done():
                    t.cancel()

        self._loop.call_soon_threadsafe(_cancel_all)

        # Shutdown async generators
        try:
            shutdown_fut = asyncio.run_coroutine_threadsafe(
                self._loop.shutdown_asyncgens(), self._loop
            )
            shutdown_fut.result(timeout=5)
        except Exception:
            pass

        # Stop and close the loop
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        self._loop.close()
        self._connect_future = None

    def get_nodes(self) -> List[NodeInfo]:
        return self._client.get_nodes()

    def get_node(self, node_id: int) -> Optional[NodeInfo]:
        return self._client.get_node(node_id)

    def get_chain_stats(self) -> Optional[ChainStats]:
        return self._client.get_chain_stats()

    def __enter__(self) -> "TelemetryClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        if self._thread.is_alive():
            logger.warning(
                "TelemetryClient was not disconnected explicitly. Cleaning up now."
            )
            self.disconnect()

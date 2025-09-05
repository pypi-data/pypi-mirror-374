import asyncio
import logging
import random
from typing import Optional, Union

import websockets

from .constants import DEFAULT_WS_URL, ChainGenesis
from .core import TelemetryEngine
from .exceptions import FeedVersionError

logger = logging.getLogger(__name__)


class AsyncTelemetryClient(TelemetryEngine):
    def __init__(
        self,
        url: str = DEFAULT_WS_URL,
        chain: Union[ChainGenesis, str] = ChainGenesis.POLKADOT,
    ):
        super().__init__()
        self.url = url
        self.chain = chain.value if isinstance(chain, ChainGenesis) else chain
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._reconnect_attempts = 0

    @property
    def is_running(self) -> bool:
        return self._running

    async def connect(self):
        """
        Establishes and maintains the WebSocket connection.

        This method runs a loop that attempts to connect and listen for messages.
        It implements an exponential backoff strategy for reconnection attempts.
        If a `FeedVersionError` is encountered, the loop will terminate permanently.
        """
        self._running = True
        while self._running:
            try:
                async with websockets.connect(self.url) as websocket:
                    self._ws = websocket
                    self._reconnect_attempts = 0
                    logger.info(f"Successfully connected to {self.url}")
                    await self._ws.send(f"subscribe:{self.chain}")
                    await self._listen()
            except FeedVersionError as e:
                logger.error(f"Critical error: {e}. Client will not run.")
                await self.disconnect()
                break
            except (websockets.exceptions.ConnectionClosed, OSError):
                logger.info("Connection closed.")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

            if self._running:
                self._reconnect_attempts += 1
                delay = min(2 ** self._reconnect_attempts, 60)
                jitter = delay / 4
                sleep_duration = delay + random.uniform(-jitter, jitter)

                logger.info(
                    f"Attempting to reconnect in {sleep_duration:.2f} seconds..."
                )
                await asyncio.sleep(sleep_duration)

    async def _listen(self):
        if not self._ws:
            return
        async for msg in self._ws:
            if not self._running:
                break
            self.process_message(msg)

    async def disconnect(self):
        self._running = False
        if self._ws:
            await self._ws.close()
            self._ws = None
        logger.info("Disconnected.")

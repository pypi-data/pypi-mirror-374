from websockets.asyncio.client import ClientConnection
from typing import Dict, Optional, Callable, Awaitable
from websockets.asyncio import client as websockets
from websockets import ConnectionClosed
from .exceptions import NexusException
from enum import Enum, IntEnum
import asyncio
import json


class OperationCode(IntEnum):
    DISPATCH = 0
    CONNECTED = 1
    AUTHENTICATE = 2
    AUTHENTICATED = 3
    PING = 6
    PONG = 7


class DispatchEventName(str, Enum):
    SOCKET_CLOSING_HINT = "SOCKET_CLOSING_HINT"


class RTS:
    def __init__(
        self,
        base_url: str,
        nexus_key: str,
        reconnect_attempts: int = 3,
    ):
        self._base_url = base_url.rstrip("/")
        self._nexus_key = nexus_key
        self._reconnect_attempts = reconnect_attempts

        self.session_code: Optional[str] = None
        self.ws: Optional[ClientConnection] = None

    async def connect(self, path: str) -> None:
        url = f"{self._base_url}{path}"

        for attempt in range(self._reconnect_attempts):
            try:
                self.ws = await websockets.connect(url, ping_timeout=None)
                return
            except Exception:
                await asyncio.sleep(1)

        raise NexusException(
            f"Failed to connect to RTS. ({self._reconnect_attempts} attempts)"
        )

    async def listen(
        self,
        handler: Optional[Callable[[dict], Awaitable[None]]] = None,
    ) -> None:
        if not self.ws:
            raise NexusException("WebSocket not connected.")

        try:
            async for message in self.ws:
                try:
                    message = json.loads(message)
                    assert isinstance(message, dict)

                    op = message.get("op")
                    data = message.get("data")

                    if op == OperationCode.CONNECTED:
                        await self.send(
                            OperationCode.AUTHENTICATE, {"key": self._nexus_key}
                        )
                        continue

                    if op == OperationCode.AUTHENTICATED:
                        continue

                    if op == OperationCode.PING:
                        await self.send(OperationCode.PONG)
                        continue

                    if op == OperationCode.DISPATCH:
                        if (
                            isinstance(data, dict)
                            and data.get("event")
                            == DispatchEventName.SOCKET_CLOSING_HINT
                        ):
                            payload = data.get("payload")
                            if isinstance(payload, dict):
                                if payload.get("code") == 1000:
                                    return

                    if handler:
                        await handler(message)

                except json.JSONDecodeError or AssertionError as e:
                    pass

        finally:
            await self.close()

    async def send(self, op: int, data: Optional[Dict] = None):
        if not self.ws:
            raise NexusException("WebSocket not connected.")

        packet = json.dumps({"op": op, "data": data})
        await self.ws.send(packet)

    async def close(self):
        if self.ws:
            await self.ws.close()

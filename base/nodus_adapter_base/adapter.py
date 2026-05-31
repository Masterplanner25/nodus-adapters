"""BaseChannelAdapter — abstract base with reconnect loop and health recording."""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from nodus_channels import Attachment, ChannelInfo, ChannelRegistry, Message
from nodus_channels.health import HealthMonitor

logger = logging.getLogger(__name__)

_RECONNECT_BACKOFF: list[float] = [1.0, 5.0, 30.0, 60.0, 300.0]


class BaseChannelAdapter(ABC):
    """Abstract base class for channel adapters.

    Provides:
    - ``connect()`` with exponential backoff retry
    - Health recording via ``HealthMonitor``
    - Default ``health_check()`` delegating to ``_do_health_check()``

    Subclass this and implement ``_do_connect``, ``_do_send``,
    ``_do_subscribe``, and optionally ``_do_health_check``.

    Usage::

        class MyAdapter(BaseChannelAdapter):
            @property
            def channel_id(self): return "my-channel"
            @property
            def info(self): return ChannelInfo("my-channel", "My Channel")
            async def _do_connect(self): ...
            async def _do_send(self, content, peer_id, **kwargs): return "msg-id"
            def _do_subscribe(self): ...
    """

    def __init__(
        self,
        *,
        health_monitor: Optional[HealthMonitor] = None,
        max_reconnect_attempts: int = 5,
    ) -> None:
        self._health = health_monitor or HealthMonitor()
        self._max_reconnect = max_reconnect_attempts
        self._connected = False

    # ── Abstract interface ────────────────────────────────────────────────────

    @property
    @abstractmethod
    def channel_id(self) -> str: ...

    @property
    @abstractmethod
    def info(self) -> ChannelInfo: ...

    @abstractmethod
    async def _do_connect(self) -> None: ...

    @abstractmethod
    async def _do_send(
        self,
        content: str,
        peer_id: str,
        *,
        thread_id: Optional[str] = None,
        reply_to_id: Optional[str] = None,
        attachments: Optional[list[Attachment]] = None,
    ) -> str: ...

    @abstractmethod
    def _do_subscribe(self) -> AsyncIterator[Message]: ...

    # ── Implemented methods ───────────────────────────────────────────────────

    async def connect(self) -> None:
        """Connect with exponential backoff retry on failure."""
        for attempt, delay in enumerate(_RECONNECT_BACKOFF[: self._max_reconnect]):
            try:
                await self._do_connect()
                self._connected = True
                self._health.record_success(self.channel_id)
                logger.info("[%s] connected", self.channel_id)
                return
            except Exception as exc:
                self._health.record_failure(self.channel_id, str(exc))
                if attempt < self._max_reconnect - 1:
                    logger.warning(
                        "[%s] connect failed (attempt %d): %s — retry in %.1fs",
                        self.channel_id, attempt + 1, exc, delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("[%s] connect failed after %d attempts: %s",
                                 self.channel_id, self._max_reconnect, exc)
                    raise

    async def disconnect(self) -> None:
        self._connected = False
        logger.info("[%s] disconnected", self.channel_id)

    async def send(
        self,
        content: str,
        peer_id: str,
        *,
        thread_id: Optional[str] = None,
        reply_to_id: Optional[str] = None,
        attachments: Optional[list[Attachment]] = None,
    ) -> str:
        try:
            msg_id = await self._do_send(
                content, peer_id,
                thread_id=thread_id,
                reply_to_id=reply_to_id,
                attachments=attachments,
            )
            self._health.record_success(self.channel_id)
            return msg_id
        except Exception as exc:
            self._health.record_failure(self.channel_id, str(exc))
            raise

    def subscribe(self) -> AsyncIterator[Message]:
        return self._do_subscribe()

    async def health_check(self) -> bool:
        try:
            result = await self._do_health_check()
            if result:
                self._health.record_success(self.channel_id)
            else:
                self._health.record_failure(self.channel_id, "health check returned False")
            return result
        except Exception as exc:
            self._health.record_failure(self.channel_id, str(exc))
            return False

    async def _do_health_check(self) -> bool:
        """Override to provide a real health check. Default: True if connected."""
        return self._connected

    @property
    def health_monitor(self) -> HealthMonitor:
        return self._health

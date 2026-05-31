"""ConnectionManager — start and stop all registered channel adapters."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from nodus_channels import ChannelRegistry

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Start and gracefully stop all adapters in a ``ChannelRegistry``.

    Usage::

        registry = ChannelRegistry()
        registry.register(MyAdapter())
        manager = ConnectionManager(registry)
        await manager.start_all()
        # ... run forever ...
        await manager.stop_all()
    """

    def __init__(self, registry: ChannelRegistry) -> None:
        self._registry = registry

    async def start_all(self) -> dict[str, bool]:
        """Connect all registered adapters concurrently.

        Returns a dict of ``{channel_id: success}`` for each adapter.
        """
        adapters = self._registry.list()
        results: dict[str, bool] = {}
        for adapter in adapters:
            try:
                await adapter.connect()
                results[adapter.channel_id] = True
            except Exception as exc:
                logger.error("[ConnectionManager] failed to connect %s: %s",
                             adapter.channel_id, exc)
                results[adapter.channel_id] = False
        return results

    async def stop_all(self) -> None:
        """Disconnect all registered adapters."""
        adapters = self._registry.list()
        for adapter in adapters:
            try:
                await adapter.disconnect()
            except Exception as exc:
                logger.warning("[ConnectionManager] error disconnecting %s: %s",
                               adapter.channel_id, exc)

    async def health_check_all(self) -> dict[str, bool]:
        """Run health_check() on all adapters.  Returns {channel_id: healthy}."""
        adapters = self._registry.list()
        results: dict[str, bool] = {}
        for adapter in adapters:
            try:
                results[adapter.channel_id] = await adapter.health_check()
            except Exception:
                results[adapter.channel_id] = False
        return results

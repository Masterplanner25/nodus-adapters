"""nodus-adapter-base tests."""
import asyncio
import pytest

from nodus_channels import ChannelInfo, ChannelRegistry, Message
from nodus_adapter_base import BaseChannelAdapter, ConnectionManager


class _StubAdapter(BaseChannelAdapter):
    """Minimal concrete adapter for testing."""

    def __init__(self, channel="test", fail_connect=False, **kw):
        super().__init__(**kw)
        self._channel = channel
        self._fail_connect = fail_connect
        self.connect_calls = 0
        self.send_calls = []

    @property
    def channel_id(self): return self._channel

    @property
    def info(self): return ChannelInfo(id=self._channel, display_name=self._channel.title())

    async def _do_connect(self):
        self.connect_calls += 1
        if self._fail_connect:
            raise ConnectionError("deliberate failure")

    async def _do_send(self, content, peer_id, **kwargs):
        self.send_calls.append((content, peer_id))
        return f"msg-{len(self.send_calls)}"

    def _do_subscribe(self):
        async def _gen():
            if False: yield  # empty async generator
        return _gen()

    async def _do_health_check(self): return self._connected


# ── connect / disconnect ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_connect_sets_connected():
    adapter = _StubAdapter()
    await adapter.connect()
    assert adapter._connected is True


@pytest.mark.asyncio
async def test_connect_records_health_success():
    adapter = _StubAdapter()
    await adapter.connect()
    snap = adapter.health_monitor.snapshot("test")
    assert snap.failure_count == 0


@pytest.mark.asyncio
async def test_connect_failure_records_health():
    adapter = _StubAdapter(fail_connect=True, max_reconnect_attempts=1)
    with pytest.raises(ConnectionError):
        await adapter.connect()
    snap = adapter.health_monitor.snapshot("test")
    assert snap.failure_count >= 1


@pytest.mark.asyncio
async def test_disconnect_clears_connected():
    adapter = _StubAdapter()
    await adapter.connect()
    await adapter.disconnect()
    assert adapter._connected is False


# ── send ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_returns_msg_id():
    adapter = _StubAdapter()
    await adapter.connect()
    msg_id = await adapter.send("hello", "peer-1")
    assert msg_id == "msg-1"
    assert adapter.send_calls[0] == ("hello", "peer-1")


@pytest.mark.asyncio
async def test_send_failure_records_health():
    class _FailSend(_StubAdapter):
        async def _do_send(self, *a, **kw):
            raise RuntimeError("send failed")

    adapter = _FailSend()
    await adapter.connect()
    with pytest.raises(RuntimeError):
        await adapter.send("hello", "peer-1")
    snap = adapter.health_monitor.snapshot("test")
    assert snap.failure_count >= 1


# ── health_check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check_true_when_connected():
    adapter = _StubAdapter()
    await adapter.connect()
    assert await adapter.health_check() is True


@pytest.mark.asyncio
async def test_health_check_false_when_disconnected():
    adapter = _StubAdapter()
    # Not connected yet
    assert await adapter.health_check() is False


# ── ConnectionManager ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_manager_start_all():
    registry = ChannelRegistry()
    registry.register(_StubAdapter("a"))
    registry.register(_StubAdapter("b"))
    manager = ConnectionManager(registry)
    results = await manager.start_all()
    assert results == {"a": True, "b": True}


@pytest.mark.asyncio
async def test_manager_start_all_partial_failure():
    registry = ChannelRegistry()
    registry.register(_StubAdapter("ok"))
    registry.register(_StubAdapter("fail", fail_connect=True, max_reconnect_attempts=1))
    manager = ConnectionManager(registry)
    results = await manager.start_all()
    assert results["ok"] is True
    assert results["fail"] is False


@pytest.mark.asyncio
async def test_manager_health_check_all():
    registry = ChannelRegistry()
    a = _StubAdapter("a")
    await a.connect()
    registry.register(a)
    manager = ConnectionManager(registry)
    results = await manager.health_check_all()
    assert results["a"] is True

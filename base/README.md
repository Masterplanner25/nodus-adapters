# nodus-adapter-base

**Abstract base class for [nodus-channels](https://github.com/Masterplanner25/nodus-channels) adapters.**

Provides the reconnect loop, health recording, and connection management
so concrete adapters (Slack, Discord, webhook, etc.) only implement the
three transport-specific methods.

> **Status:** v0.1.0 — prepared, not yet published.

---

## Install

```bash
pip install nodus-adapter-base
```

Requires `nodus-channels>=0.1.0`.

---

## What it provides

| Class | Purpose |
|---|---|
| `BaseChannelAdapter` | Abstract base with `connect()` retry backoff, health recording, `send()`, `subscribe()` |
| `ConnectionManager` | `start_all()`, `stop_all()`, `health_check_all()` across a `ChannelRegistry` |

---

## Implementing an adapter

```python
from nodus_channels import ChannelInfo, Message
from nodus_adapter_base import BaseChannelAdapter

class SlackAdapter(BaseChannelAdapter):
    @property
    def channel_id(self) -> str:
        return "slack"

    @property
    def info(self) -> ChannelInfo:
        return ChannelInfo(id="slack", display_name="Slack")

    async def _do_connect(self) -> None:
        # establish websocket / API connection
        ...

    async def _do_send(self, content, peer_id, *, thread_id=None,
                       reply_to_id=None, attachments=None) -> str:
        # send message; return message ID
        return "slack-msg-id"

    def _do_subscribe(self):
        # return an async generator yielding Message objects
        async def _gen():
            ...
            yield message
        return _gen()
```

### Reconnect backoff

`connect()` retries up to `max_reconnect_attempts` times (default 5) using
the backoff schedule `[1, 5, 30, 60, 300]` seconds. Each failure is recorded
on the `HealthMonitor`. Raises the last exception if all attempts fail.

### Health recording

Every `connect()`, `send()`, and `health_check()` call records success or
failure on the adapter's `HealthMonitor`. Access it via `adapter.health_monitor`.

---

## ConnectionManager

```python
from nodus_channels import ChannelRegistry
from nodus_adapter_base import ConnectionManager

registry = ChannelRegistry()
registry.register(SlackAdapter())
registry.register(DiscordAdapter())

manager = ConnectionManager(registry)
results = await manager.start_all()        # {"slack": True, "discord": True}
health  = await manager.health_check_all() # {"slack": True, "discord": False}
await manager.stop_all()
```

---

## Development

```bash
cd base
pip install -e ".[dev]"
pytest tests/ -q
```

---

## License

MIT — see [LICENSE](../LICENSE).

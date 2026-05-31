"""nodus-adapter-base — abstract base for channel adapters.

BaseChannelAdapter:
    - connect() with exponential backoff retry
    - Health recording via HealthMonitor
    - Abstract interface: _do_connect, _do_send, _do_subscribe

ConnectionManager:
    - start_all() / stop_all() / health_check_all()
"""
from .adapter import BaseChannelAdapter
from .manager import ConnectionManager

__all__ = ["BaseChannelAdapter", "ConnectionManager"]

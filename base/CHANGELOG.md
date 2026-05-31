# Changelog — nodus-adapter-base

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-05-30

Initial release — prepared, not yet published.

### Added

- **BaseChannelAdapter** — abstract base class for channel adapters.
  `connect()` with exponential backoff (`[1, 5, 30, 60, 300]` seconds,
  configurable `max_reconnect_attempts`). Health recording via `HealthMonitor`
  on every connect, send, and health-check call. Abstract interface:
  `_do_connect`, `_do_send`, `_do_subscribe`, `_do_health_check`.
  Concrete `send()`, `subscribe()`, `disconnect()`, `health_check()`.

- **ConnectionManager** — orchestrates a `ChannelRegistry` of adapters.
  `start_all()` connects all registered adapters concurrently; returns
  `{channel_id: bool}` success map. `stop_all()` disconnects all.
  `health_check_all()` runs health checks concurrently.

- **11 tests** covering connect, disconnect, send, health check, and
  `ConnectionManager` start/partial-failure/health scenarios.

- **Single dependency:** `nodus-channels>=0.1.0` (for `ChannelRegistry`,
  `ChannelInfo`, `Message`, `Attachment`, `HealthMonitor`).

[0.1.0]: https://github.com/Masterplanner25/nodus-adapters/releases/tag/base-v0.1.0

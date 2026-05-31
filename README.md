# nodus-adapters

**Monorepo for [nodus-channels](https://github.com/Masterplanner25/nodus-channels) adapter implementations.**

Each adapter is an independent package in its own subdirectory.

---

## Packages

| Package | Path | Description |
|---|---|---|
| `nodus-adapter-base` | [`base/`](base/) | Abstract base class with reconnect loop, health recording, and connection manager |

---

## Adding a new adapter

1. Create a new subdirectory: `adapters/<name>/`
2. Add `pyproject.toml`, `nodus_adapter_<name>/`, and `tests/`
3. Depend on `nodus-adapter-base` and `nodus-channels`
4. Implement `BaseChannelAdapter` from `nodus_adapter_base`

---

## License

MIT — see [LICENSE](LICENSE).

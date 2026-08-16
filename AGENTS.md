# Maintainer and agent instructions

This repository contains a standalone Hermes Agent plugin. Keep it installable by Hermes directly from the repository root.

## Invariants

- `plugin.yaml` and `__init__.py` stay at repository root.
- Real Discord guild, channel, thread, user, and role IDs belong only in profile configuration.
- Configured channels must remain outside Hermes `free_response_channels`; otherwise the core adapter deliberately skips auto-threading.
- Existing sender authorization, allowed-channel, ignored-channel, and thread-failure behavior must remain intact.
- Event-local routing state must use `ContextVar`; never replace it with mutable global or adapter-instance state.
- An empty configuration remains inert and must not patch the adapter.
- Never commit `$HERMES_HOME`, profile configuration, Discord tokens, IDs, messages, logs, credentials, or machine-specific paths.
- Use synthetic IDs and payloads in tests.

## Verification

Run tests and Ruff against both the pinned compatible Hermes commit and current upstream where possible. Include target-parent, inherited-thread, unrelated-channel, empty-configuration, and concurrent-message coverage.

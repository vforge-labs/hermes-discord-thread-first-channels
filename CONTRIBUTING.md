# Contributing

Contributions are welcome, especially compatibility fixes for newer Hermes Agent Discord adapters and additional routing-isolation tests.

## Ground rules

- Never include real Discord IDs, message content, profile paths, tokens, logs, or `$HERMES_HOME` contents in issues, fixtures, or commits.
- Preserve existing sender and channel authorization gates.
- Keep configured channels out of Hermes `free_response_channels` so the normal auto-thread path remains active.
- Use context-local event state; concurrent messages must not leak routing policy.
- Keep an unconfigured installation inert.
- Use synthetic IDs and payloads in tests.

## Development setup

Clone this repository and a compatible Hermes Agent checkout:

```bash
git clone https://github.com/vforge-labs/hermes-discord-thread-first-channels
git clone https://github.com/NousResearch/hermes-agent
cd hermes-discord-thread-first-channels
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip pytest ruff
```

Run the harness:

```bash
python -m pytest
ruff check .
```

## Pull requests

Include the Hermes commit(s) tested, tests added or updated, Discord adapter compatibility notes, and confirmation that fixtures contain synthetic data only.

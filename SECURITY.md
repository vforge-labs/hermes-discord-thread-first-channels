# Security Policy

## Supported versions

Security fixes are applied to the latest release and the `main` branch.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting / Security Advisories for this repository. Do not open a public issue containing exploit details, tokens, Discord identifiers, message content, or private profile configuration.

Include:

- affected plugin and Hermes versions;
- minimal reproduction steps using synthetic IDs and messages;
- whether the issue crosses channel, thread, user, or concurrent-event boundaries;
- impact and any known mitigations.

## Security boundaries

This plugin changes mention and thread-routing behavior for explicitly configured parent channels. It does not bypass Hermes sender authorization, allowed-channel policy, ignored-channel policy, or Discord permissions. It is not an operating-system or Discord-account sandbox.

See [`docs/security-model.md`](docs/security-model.md) for the detailed boundary model.

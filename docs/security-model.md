# Security model

`hermes-discord-thread-first-channels` is a narrow routing-policy patch for Hermes Agent's Discord adapter.

## What it changes

For each explicitly configured parent channel, the plugin handles that event as mention-free while removing the same channel from the adapter's free-response set. Hermes can therefore accept an unmentioned top-level request and still execute its normal auto-thread creation path. Child threads inherit their parent channel's policy.

## What it does not change

The plugin does not:

- authorize Discord users, roles, guilds, or channels;
- change allowed-channel or ignored-channel gates;
- grant Discord permissions;
- send messages outside Hermes' normal adapter path;
- suppress Hermes' fail-closed behavior when thread creation fails;
- register or override model tools;
- store tokens, IDs, messages, or session history.

## Configuration boundary

Real channel IDs belong in the active profile's `config.yaml` under:

```yaml
plugins:
  entries:
    hermes-discord-thread-first-channels:
      channel_ids:
        - "123456789012345678"
```

Configured channels must not also appear in `discord.free_response_channels` or `DISCORD_FREE_RESPONSE_CHANNELS`; Hermes deliberately treats those as inline chat surfaces and skips auto-threading.

## Concurrency boundary

Discord events can be processed concurrently. The plugin uses a Python `ContextVar` around each `_handle_message` invocation so target-channel policy cannot leak into an unrelated event. Mutable module globals or adapter-instance flags are not acceptable substitutes.

## Compatibility boundary

The plugin relies on internal Discord adapter methods: `_handle_message`, `_discord_require_mention`, and `_discord_free_response_channels`. Operators should run the test harness after Hermes upgrades and keep the plugin inert until compatibility is confirmed when those methods change.

# hermes-discord-thread-first-channels

A profile-local [Hermes Agent](https://hermes-agent.nousresearch.com) plugin for Discord channels that should accept messages without an `@mention` **and** keep every new top-level conversation in its own thread.

## Why this exists

Hermes intentionally treats `discord.free_response_channels` as inline chat surfaces. Those channels skip auto-threading. That is useful for ordinary bot-chat rooms, but it cannot express a channel policy of:

- no mention required for a new request;
- create a thread from each top-level request;
- continue naturally inside that thread;
- leave all other Discord channels unchanged.

This plugin supplies that narrow policy without modifying Hermes core.

## Installation

```bash
hermes plugins install vforge-labs/hermes-discord-thread-first-channels
hermes plugins enable hermes-discord-thread-first-channels --no-allow-tool-override
```

## Configuration

Configure one channel ID or a comma-separated list in the active profile:

```bash
hermes config set \
  plugins.entries.hermes-discord-thread-first-channels.channel_ids \
  '123456789012345678,234567890123456789'
```

Equivalent YAML shape:

```yaml
plugins:
  entries:
    hermes-discord-thread-first-channels:
      channel_ids:
        - "123456789012345678"
        - "234567890123456789"
```

Keep these channels out of both `discord.free_response_channels` and `DISCORD_FREE_RESPONSE_CHANNELS`. Recommended Discord settings:

```yaml
discord:
  require_mention: true
  auto_thread: true
  thread_require_mention: false
```

Restart the profile gateway after enabling or changing the plugin.

## Behavior

For configured parent channels, the plugin temporarily makes the current event mention-free while excluding the channel from the adapter's free-response set. Hermes then follows its normal, verified auto-thread route. Child threads inherit their parent channel's policy.

The event-local state uses Python `ContextVar`, so concurrent target and non-target Discord messages do not leak routing policy into each other.

## Security and scope

- No Discord tokens, guild IDs, channel IDs, hostnames, or user data are built in.
- The plugin patches only the active process' Discord adapter class.
- It does not register or override model tools.
- Unconfigured installations remain inert.
- Existing sender authorization and allowed-channel gates remain in force.

## Verification

```bash
python -m unittest discover -s tests -v
python -m py_compile __init__.py tests/test_thread_first.py
```

## Compatibility

Built for Hermes Agent versions whose Discord adapter exposes `_handle_message`, `_discord_require_mention`, and `_discord_free_response_channels`. These are internal adapter methods; run the tests after Hermes upgrades.

## License

Apache-2.0

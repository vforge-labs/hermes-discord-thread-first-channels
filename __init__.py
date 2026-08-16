"""Mention-free Discord channels that retain Hermes auto-threading.

Hermes normally treats ``free_response_channels`` as inline chat surfaces and
therefore skips auto-thread creation for them. This plugin lets selected parent
channels accept unmentioned messages while preserving the normal auto-thread
path. Channel IDs are read from profile-local configuration; none are built
into the plugin.
"""

from __future__ import annotations

import contextvars
import logging
from collections.abc import Iterable
from typing import Any

logger = logging.getLogger(__name__)

PLUGIN_ID = "hermes-discord-thread-first-channels"
_thread_first_active: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "discord_thread_first_active", default=False
)


def _parse_channel_ids(raw: Any) -> frozenset[str]:
    """Normalize a YAML list or comma-separated scalar into channel IDs."""
    if raw is None:
        return frozenset()
    values = raw if isinstance(raw, (list, tuple, set, frozenset)) else str(raw).split(",")
    return frozenset(str(value).strip() for value in values if str(value).strip())


def _configured_channel_ids(config: dict[str, Any] | None = None) -> frozenset[str]:
    """Read ``plugins.entries.<plugin>.channel_ids`` from active-profile config."""
    if config is None:
        from hermes_cli.config import load_config

        config = load_config() or {}
    plugins = config.get("plugins") or {}
    entries = plugins.get("entries") or {}
    entry = entries.get(PLUGIN_ID) or {}
    return _parse_channel_ids(entry.get("channel_ids"))


def _message_channel_ids(message: Any) -> set[str]:
    """Return the current channel ID and parent ID, when present."""
    channel = getattr(message, "channel", None)
    ids: set[str] = set()
    channel_id = getattr(channel, "id", None)
    if channel_id is not None:
        ids.add(str(channel_id))

    parent_id = getattr(channel, "parent_id", None)
    if parent_id is None:
        parent = getattr(channel, "parent", None)
        parent_id = getattr(parent, "id", None)
    if parent_id is not None:
        ids.add(str(parent_id))
    return ids


def install_adapter_patch(adapter_cls: type, channel_ids: Iterable[str]) -> bool:
    """Patch one Discord adapter class once; return whether installation occurred."""
    if getattr(adapter_cls, "_thread_first_channels_patch", False):
        return False

    targets = frozenset(str(item).strip() for item in channel_ids if str(item).strip())
    if not targets:
        return False

    original_handle = adapter_cls._handle_message
    original_require_mention = adapter_cls._discord_require_mention
    original_free_channels = adapter_cls._discord_free_response_channels

    async def _handle_message(self, message, *args, **kwargs):
        active = bool(_message_channel_ids(message) & targets)
        token = _thread_first_active.set(active)
        try:
            return await original_handle(self, message, *args, **kwargs)
        finally:
            _thread_first_active.reset(token)

    def _discord_require_mention(self):
        if _thread_first_active.get():
            return False
        return original_require_mention(self)

    def _discord_free_response_channels(self):
        channels = set(original_free_channels(self))
        if _thread_first_active.get():
            channels.difference_update(targets)
        return channels

    adapter_cls._handle_message = _handle_message
    adapter_cls._discord_require_mention = _discord_require_mention
    adapter_cls._discord_free_response_channels = _discord_free_response_channels
    adapter_cls._thread_first_channels_patch = True
    adapter_cls._thread_first_channels_targets = targets
    return True


def register(ctx) -> None:
    channel_ids = _configured_channel_ids()
    if not channel_ids:
        logger.warning(
            "%s is enabled but no channel_ids are configured; plugin remains inert",
            PLUGIN_ID,
        )
        return

    try:
        from plugins.platforms.discord.adapter import DiscordAdapter
    except Exception as exc:  # pragma: no cover - runtime dependency diagnostics
        logger.warning("Discord thread-first patch unavailable: %s", exc)
        return

    installed = install_adapter_patch(DiscordAdapter, channel_ids)
    logger.info(
        "Discord thread-first patch %s for %d configured channel(s)",
        "installed" if installed else "already active",
        len(channel_ids),
    )

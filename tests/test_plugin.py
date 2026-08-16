"""Tests for thread-first Discord channel routing."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from collections.abc import Generator
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
TARGET = "123456789012345678"
OTHER = "987654321098765432"


@pytest.fixture
def plugin() -> Generator[ModuleType, None, None]:
    name = "_discord_thread_first_plugin_test"
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    implementation = sys.modules[f"{name}.hermes_discord_thread_first_channels"]
    try:
        yield implementation
    finally:
        sys.modules.pop(name, None)
        sys.modules.pop(f"{name}.hermes_discord_thread_first_channels", None)


@pytest.fixture
def fake_adapter() -> type:
    class FakeAdapter:
        def _discord_require_mention(self):
            return True

        def _discord_free_response_channels(self):
            return {TARGET, OTHER}

        async def _handle_message(self, message, *, pause=None):
            if pause:
                await pause.wait()
            return self._discord_require_mention(), self._discord_free_response_channels()

    return FakeAdapter


def message(channel_id: str, parent_id: str | None = None):
    return SimpleNamespace(
        channel=SimpleNamespace(id=channel_id, parent_id=parent_id, parent=None)
    )


def test_parse_list_and_csv(plugin: ModuleType) -> None:
    assert plugin._parse_channel_ids([TARGET, OTHER]) == {TARGET, OTHER}
    assert plugin._parse_channel_ids(f"{TARGET}, {OTHER}") == {TARGET, OTHER}


def test_reads_plugin_entry(plugin: ModuleType) -> None:
    config = {
        "plugins": {
            "entries": {
                plugin.PLUGIN_ID: {"channel_ids": [TARGET, OTHER]},
            }
        }
    }
    assert plugin._configured_channel_ids(config) == {TARGET, OTHER}


def test_empty_configuration_is_inert(plugin: ModuleType, fake_adapter: type) -> None:
    assert plugin.install_adapter_patch(fake_adapter, set()) is False
    assert not getattr(fake_adapter, "_thread_first_channels_patch", False)


def test_target_parent_is_mention_free_but_not_free_response(
    plugin: ModuleType, fake_adapter: type
) -> None:
    plugin.install_adapter_patch(fake_adapter, {TARGET})
    required, free = asyncio.run(fake_adapter()._handle_message(message(TARGET)))
    assert required is False
    assert TARGET not in free
    assert OTHER in free


def test_child_thread_inherits_target_parent_policy(
    plugin: ModuleType, fake_adapter: type
) -> None:
    plugin.install_adapter_patch(fake_adapter, {TARGET})
    required, free = asyncio.run(
        fake_adapter()._handle_message(message("thread-id", parent_id=TARGET))
    )
    assert required is False
    assert TARGET not in free


def test_other_channels_keep_original_policy(plugin: ModuleType, fake_adapter: type) -> None:
    plugin.install_adapter_patch(fake_adapter, {TARGET})
    required, free = asyncio.run(fake_adapter()._handle_message(message(OTHER)))
    assert required is True
    assert free == {TARGET, OTHER}


def test_context_is_isolated_between_concurrent_messages(
    plugin: ModuleType, fake_adapter: type
) -> None:
    plugin.install_adapter_patch(fake_adapter, {TARGET})
    pause = asyncio.Event()

    async def run_both():
        target_task = asyncio.create_task(
            fake_adapter()._handle_message(message(TARGET), pause=pause)
        )
        other_task = asyncio.create_task(
            fake_adapter()._handle_message(message(OTHER), pause=pause)
        )
        await asyncio.sleep(0)
        pause.set()
        return await asyncio.gather(target_task, other_task)

    target_result, other_result = asyncio.run(run_both())
    assert target_result[0] is False
    assert other_result[0] is True

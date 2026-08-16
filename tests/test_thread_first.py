from __future__ import annotations

import asyncio
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

PLUGIN = Path(__file__).resolve().parents[1] / "__init__.py"
spec = importlib.util.spec_from_file_location("thread_first_test_plugin", PLUGIN)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

TARGET = "123456789012345678"
OTHER = "987654321098765432"


class FakeAdapter:
    def _discord_require_mention(self):
        return True

    def _discord_free_response_channels(self):
        return {TARGET, OTHER}

    async def _handle_message(self, message, *, pause=None):
        if pause:
            await pause.wait()
        return self._discord_require_mention(), self._discord_free_response_channels()


def message(channel_id: str, parent_id: str | None = None):
    return SimpleNamespace(
        channel=SimpleNamespace(id=channel_id, parent_id=parent_id, parent=None)
    )


class ConfigurationTests(unittest.TestCase):
    def test_parse_list_and_csv(self):
        self.assertEqual(module._parse_channel_ids([TARGET, OTHER]), {TARGET, OTHER})
        self.assertEqual(module._parse_channel_ids(f"{TARGET}, {OTHER}"), {TARGET, OTHER})

    def test_reads_plugin_entry(self):
        config = {
            "plugins": {
                "entries": {
                    module.PLUGIN_ID: {"channel_ids": [TARGET, OTHER]},
                }
            }
        }
        self.assertEqual(module._configured_channel_ids(config), {TARGET, OTHER})


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module.install_adapter_patch(FakeAdapter, {TARGET})

    def test_target_parent_is_mention_free_but_not_free_response(self):
        required, free = asyncio.run(FakeAdapter()._handle_message(message(TARGET)))
        self.assertFalse(required)
        self.assertNotIn(TARGET, free)
        self.assertIn(OTHER, free)

    def test_child_thread_inherits_target_parent_policy(self):
        required, free = asyncio.run(
            FakeAdapter()._handle_message(message("thread-id", parent_id=TARGET))
        )
        self.assertFalse(required)
        self.assertNotIn(TARGET, free)

    def test_other_channels_keep_original_policy(self):
        required, free = asyncio.run(FakeAdapter()._handle_message(message(OTHER)))
        self.assertTrue(required)
        self.assertEqual(free, {TARGET, OTHER})

    def test_context_is_isolated_between_concurrent_messages(self):
        pause = asyncio.Event()

        async def run_both():
            target_task = asyncio.create_task(
                FakeAdapter()._handle_message(message(TARGET), pause=pause)
            )
            other_task = asyncio.create_task(
                FakeAdapter()._handle_message(message(OTHER), pause=pause)
            )
            await asyncio.sleep(0)
            pause.set()
            return await asyncio.gather(target_task, other_task)

        target_result, other_result = asyncio.run(run_both())
        self.assertFalse(target_result[0])
        self.assertTrue(other_result[0])


if __name__ == "__main__":
    unittest.main()

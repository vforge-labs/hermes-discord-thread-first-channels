# Contributing

Contributions are welcome.

1. Fork the repository and create a focused branch.
2. Keep the plugin profile-local and avoid Hermes core patches.
3. Do not commit Discord tokens, real guild/channel/user IDs, private hostnames, or runtime state.
4. Run:

   ```bash
   python -m unittest discover -s tests -v
   python -m py_compile __init__.py tests/test_thread_first.py
   ```

5. Describe compatibility assumptions and routing/security impact in the pull request.

The plugin intentionally relies on internal Discord adapter methods. Changes should remain narrow and preserve unrelated channel behavior.

# Repository guidance

This repository contains a user-space Hermes Agent plugin. Prefer configuration and plugin behavior over Hermes core modifications.

Before committing:

- run the standard-library unit tests and `py_compile`;
- scan for credentials, real Discord IDs, private hostnames, generated caches, and runtime state;
- keep the root direct-install contract (`plugin.yaml` plus root `__init__.py`);
- use synthetic identifiers in tests and documentation;
- preserve unrelated Discord authorization and routing behavior.

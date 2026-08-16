"""Hermes registration shim for thread-first Discord channel routing."""

if __package__:
    from .hermes_discord_thread_first_channels import register
else:  # pytest may collect a root __init__.py outside package context
    from hermes_discord_thread_first_channels import register

__all__ = ["register"]

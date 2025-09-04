import importlib


__all__ = 'CommandError', 'get_command'


class CommandError(Exception):
    """Generic command error."""


def get_command(name: str):
    """
    Return command function by its name.

    This is mainly used to provide commands on-demand to avoid
    import-the-world delay in CLI.
    """

    module = importlib.import_module(f'.{name}', __package__)
    return getattr(module, 'run')

from .__version__ import __version__

__all__ = ["EmailNotifier", "__version__"]

def __getattr__(name: str):
    if name == "EmailNotifier":
        from .notifier import EmailNotifier
        return EmailNotifier
    raise AttributeError(name)

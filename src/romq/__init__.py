import importlib.metadata

from romq.app import errors, nes

__all__ = ("errors", "nes")

__version__ = importlib.metadata.version(__name__)

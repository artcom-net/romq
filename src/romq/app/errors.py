class RomqError(Exception):
    """Base exception for all ROMQ errors."""


class RomIOError(RomqError):
    """Raised when a ROM file cannot be read or accessed."""


class RomInspectError(RomqError):
    """Raised when a ROM is invalid or cannot be parsed."""

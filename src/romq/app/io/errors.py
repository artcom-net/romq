from romq.app.errors import RomIOError


class ArchiveError(RomIOError):
    """Raised when the archive is invalid or cannot be processed."""


class ArchiveMissingRom(RomIOError):
    """Raised when the archive contains no matching ROM file."""

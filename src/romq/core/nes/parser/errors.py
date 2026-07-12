from romq.core.nes.errors import NesError


class ParseError(NesError):
    """Base exception for ROM parsing errors."""


class HeaderParseError(ParseError):
    """Raised when the NES header cannot be read or decoded."""


class InvalidHeaderError(HeaderParseError):
    """Raised when the NES magic bytes are invalid."""


class UnknownRomError(ParseError):
    """Raised when a ROM format is not recognized."""


class UnsupportedRomError(ParseError):
    """Raised when a ROM format is identified but not supported."""

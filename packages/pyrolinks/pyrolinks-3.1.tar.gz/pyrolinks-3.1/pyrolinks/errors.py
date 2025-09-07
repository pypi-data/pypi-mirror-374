class PyroLinksError(Exception):
    """Base class for all PyroLinks errors."""
pass


class InvalidParameterError(PyroLinksError):
    """Raised when invalid query parameters are provided."""
    pass


class InvalidMediaError(PyroLinksError):
    """Raised when the message does not contain a downloadable media."""
    pass


class FileStreamError(PyroLinksError):
    """Raised when streaming a file fails."""
pass


class ServerError(PyroLinksError):
    """Raised when the internal server faces an unexpected error."""
pass

class UtilsError(PyroLinksError):
    """Raised when something fails in utils.py"""
    pass


class LinkGenerationError(PyroLinksError):
    """Raised when generating a download link fails."""
pass

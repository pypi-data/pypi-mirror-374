class NoIncomingException(Exception):
    """Thrown when no incoming message is available"""

    pass


class ErrorMessageException(Exception):
    """Thrown when an error message is received"""

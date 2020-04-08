class LambdaCacheError(Exception):
    """Base class for exceptions in this module."""

    pass


class ArgumentTypeNotSupportedError(LambdaCacheError):
    """Raised when Argument is not supported by the function."""

    def __init__(self, message):
        self.message = message
        self.Code = "ArgumentTypeNotSupportedError"


class NoEntryNameError(LambdaCacheError):
    """Raised when No entry_name is provided."""

    def __init__(self, message=False):
        self.message = "No entry_name provided"
        self.Code = "ArgumentTypeNotSupportedError"

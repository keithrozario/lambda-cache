class LambdaCacheError(Exception):
    """Base class for exceptions in this module."""

    pass


class ArgumentTypeNotSupportedError(LambdaCacheError):
    """
    Raised when Argument is not one of the following:
        String, List of Strings, Dict with no nested dicts.
    """

    def __init__(self, message=False):
        self.message = "Only arguments of type str or list of strs supported"
        self.Code = "ArgumentTypeNotSupportedError"


class NoEntryNameError(LambdaCacheError):
    """
    Raised when No entry_name is provided
    """

    def __init__(self, message=False):
        self.message = "No entry_name provided"
        self.Code = "ArgumentTypeNotSupportedError"

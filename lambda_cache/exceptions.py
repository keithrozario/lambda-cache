class LambdaCacheError(Exception):

    """
    Base class for exceptions in this module.
    """

    pass


class ArgumentTypeNotSupportedError(LambdaCacheError):

    """
    Raised when Argument is not supported by the function.
    """

    def __init__(self, message):
        self.message = message
        self.Code = "ArgumentTypeNotSupportedError"


class NoEntryNameError(LambdaCacheError):

    """
    Raised when No entry_name is provided.
    """

    def __init__(self, message=False):
        self.message = "No entry_name provided"
        self.Code = "NoEntryNameError"


class InvalidS3UriError(LambdaCacheError):

    """
    s3Uri provided in invalid format
    """

    def __init__(self, invalid_uri):
        self.message = f"Expected Valid s3uri of the form 's3://bucket-name/path/to/file', given: {invalid_uri}"
        self.Code = "InvalidS3UriError"

import boto3
from datetime import datetime, timezone

from .caching_logic import get_decorator, get_value
from .exceptions import InvalidS3UriError


def cache(
    s3Uri: str, max_age_in_seconds=60, entry_name=False, check_before_download=True
):
    """
    Calls parameter caching, and decorates function by injecting key value into the context object

    Args:
        s3Uri(string): S3 Uri of file to download
        max_age_in_seconds(int) : Time to Live of the parameter in seconds
        entry_name(str) : Name of entry in cache
        check_before_download (boolean): Check object age before downloading
    Returns:
        decorate         : Decorated function

    """

    decorator = get_decorator(
        argument=s3Uri,
        max_age_in_seconds=max_age_in_seconds,
        entry_name=entry_name,
        miss_function=get_object_from_s3,
        check_before_download=check_before_download,
        send_details=True,  # specifies to send all details to miss_function
        s3Uri=s3Uri,
    )
    return decorator


def get_entry(
    s3Uri: str, max_age_in_seconds=60, entry_name=False, check_before_download=True
):
    """
    Wrapper function for parameter_caching

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
        max_age_in_seconds(int) : Time to Live of the parameter in seconds
        var_name(string) : Optional name of parameter to inject into context object

    Returns:
        parameter_value(string)  : Value of the parameter
    """

    file_location = get_value(
        argument=s3Uri,
        max_age_in_seconds=max_age_in_seconds,
        entry_name=entry_name,
        miss_function=get_object_from_s3,
        check_before_download=check_before_download,
        send_details=True,  # specifies to send all details to miss_function
        s3Uri=s3Uri,
    )

    return file_location


def get_object_from_s3(**kwargs):

    """
    Gets parameter value from the System manager Parameter store

    Args:
        kwargs['s3Uri']: Uri of S3 object in the form of s3://bucket-name/path/to/object
        kwargs['entry_name']: Name of entry in cache
        kwargs['entry_age_in_seconds']: Age of cache entry
    Returns:
        file_location (str): location of file on file-system (e.g. /tmp/example.txt)

    """
    s3_uri = kwargs["s3Uri"]
    bucket_name, key = parse_s3_uri(s3_uri)
    file_location = f"/tmp/{kwargs['entry_name']}"

    s3 = boto3.resource("s3")
    s3_object = s3.Object(bucket_name, key)

    if kwargs["check_before_download"] and kwargs["entry_age_in_seconds"] is not None:
        last_modified = s3_object.last_modified
        now = datetime.now(timezone.utc)
        object_age_in_seconds = (now - last_modified).seconds

        # if the object is older than the entry_age
        if object_age_in_seconds > kwargs["entry_age_in_seconds"]:
            return file_location

    s3_object.download_file(file_location)

    return file_location


def parse_s3_uri(s3_uri):

    elements = s3_uri.split("/")

    if elements[0] != "s3:" or elements[1] != "":
        raise InvalidS3UriError(s3_uri)
    else:
        bucket_name = elements[2]
        key = "/".join(elements[3:])

    return bucket_name, key

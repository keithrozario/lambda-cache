import functools
import boto3

from .caching_logic import check_cache, get_entry_name
from .exceptions import ArgumentTypeNotSupportedError


def secret_cache(name, ttl_seconds=60, entry_name=False):
    """
    Calls check cache, and decorates function by injecting key value into the context object
        ** The secret name must be ASCII letters, digits, or the following characters : /_+=.@-
    Args:
        name(string)     : Name of the secret (or ARN)
        ttl_seconds(int) : Time to Live of the parameter in seconds
        var_name(string) : Optional name of parameter to inject into context object

    Returns:
        decorate         : Decorated function

    """

    def decorator(func):
        @functools.wraps(func)
        def inner_function(event, context):

            response = check_cache(
                argument=name,
                ttl_seconds=ttl_seconds,
                entry_name=entry_name,
                miss_function=get_secret_from_secrets_manager,
            )
            # Inject {parameter_name: parameter_value} into context object
            context.update(response)

            return func(event, context)

        return inner_function

    return decorator


def get_secret_cache(name, ttl_seconds=60, entry_name=False):
    """
    Wrapper function for parameter_caching

    Args:
        name(string): Name of the parameter in System Manager Parameter Store
        ttl_seconds(int) : Time to Live of the parameter in seconds
        var_name(string) : Optional name of parameter to inject into context object

    Returns:
        parameter_value(string)  : Value of the parameter
    """

    response = check_cache(
        argument=name,
        ttl_seconds=ttl_seconds,
        entry_name=entry_name,
        miss_function=get_secret_from_secrets_manager,
    )
    parameter_value = list(response.values())[0]
    return parameter_value


def get_secret_from_secrets_manager(name):
    """
    Gets parameter value from the System manager Parameter store

    Args:
        name(string): Name of the secret or ARN of secret
    Returns:
        secret_value (string/binary): Value of secret in secrets manager in either String or Binary format
    """

    if isinstance(name, str):
        secrets_client = boto3.client("secretsmanager")
        response = secrets_client.get_secret_value(SecretId=name)
        if response.get("SecretString") is not None:
            return_value = response["SecretString"]
        else:
            return_value = response["SecretBinary"]
    else:
        raise ArgumentTypeNotSupportedError(
            f"Secrets Manager only supports str arguments: {name} is not a string"
        )

    return return_value

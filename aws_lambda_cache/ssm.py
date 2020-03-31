import functools
import boto3

from .caching_logic import check_cache


def ssm_cache(parameter, ttl_seconds=60, var_name=False):
    """
    Calls parameter caching, and decorates function by injecting key value into the event object

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
        ttl_seconds(int) : Time to Live of the parameter in seconds
        var_name(string) : Optional name of parameter to inject into event object

    Returns:
        decorate         : Decorated function

    """

    def decorator(func):
        @functools.wraps(func)
        def inner_function(event, context):

            response = check_cache(
                parameter=parameter,
                ttl_seconds=ttl_seconds,
                entry_name=var_name,
                miss_function=get_parameter_from_ssm,
            )
            # Inject {parameter_name: parameter_value} into event dict
            event.update(response)

            return func(event, context)

        return inner_function

    return decorator


def get_ssm_cache(parameter, ttl_seconds=60, var_name=False):
    """
    Wrapper function for parameter_caching

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
        ttl_seconds(int) : Time to Live of the parameter in seconds
        var_name(string) : Optional name of parameter to inject into event object

    Returns:
        parameter_value(string)  : Value of the parameter
    """

    response = check_cache(
        parameter=parameter,
        ttl_seconds=ttl_seconds,
        entry_name=var_name,
        miss_function=get_parameter_from_ssm,
    )
    parameter_value = list(response.values())[0]
    return parameter_value


def get_parameter_from_ssm(parameter):
    """
    Gets parameter value from the System manager Parameter store

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
    Returns:
        parameter_value (string): Value of parameter in Parameter Store
    """

    ssm_client = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=parameter, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]

    # return StringList
    if response["Parameter"]["Type"] == "StringList":
        parameter_value = parameter_value.split(",")

    return parameter_value

import boto3

from .caching_logic import get_decorator, get_value, get_entry_name
from .exceptions import ArgumentTypeNotSupportedError

default_max_age_in_seconds = 60


def cache(
    parameter: str, max_age_in_seconds=default_max_age_in_seconds, entry_name=False
):
    """
    Calls parameter caching, and decorates function by injecting key value into the context object

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
        max_age_in_seconds(int) : Time to Live of the parameter in seconds
        var_name(string) : Optional name of parameter to inject into context object

    Returns:
        decorate         : Decorated function

    """

    decorator = get_decorator(
        argument=parameter,
        max_age_in_seconds=max_age_in_seconds,
        entry_name=entry_name,
        miss_function=get_parameter_from_ssm,
    )
    return decorator


def get_entry(
    parameter: str, max_age_in_seconds=default_max_age_in_seconds, entry_name=False
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

    parameter_value = get_value(
        argument=parameter,
        max_age_in_seconds=max_age_in_seconds,
        entry_name=entry_name,
        miss_function=get_parameter_from_ssm,
    )
    return parameter_value


def get_parameter_from_ssm(parameter):
    """
    Gets parameter value from the System manager Parameter store

    Args:
        parameter(string / list): Name of the parameter(s) in System Manager Parameter Store
    Returns:
        parameter_value (string): Single Value of parameter in Parameter Store; or
        parameters (list): List of Values from Parameter Store
    """

    ssm_client = boto3.client("ssm")

    if isinstance(parameter, str):
        response = ssm_client.get_parameter(Name=parameter, WithDecryption=True)
        parameter_value = response["Parameter"]["Value"]
        # return StringList
        if response["Parameter"]["Type"] == "StringList":
            parameter_value = parameter_value.split(",")
        return_value = parameter_value

    elif isinstance(parameter, list):
        response = ssm_client.get_parameters(Names=parameter, WithDecryption=True)
        parameters = {}
        for param in response["Parameters"]:
            param_name = get_entry_name(param["Name"], False)
            if param["Type"] == "StringList":
                parameters[param_name] = param["Value"].split(",")
            else:
                parameters[param_name] = param["Value"]
        return_value = parameters

    else:
        raise ArgumentTypeNotSupportedError(
            "Only str or list supported for ssm, {parameter} is of type: {type(parameter)}"
        )

    return return_value

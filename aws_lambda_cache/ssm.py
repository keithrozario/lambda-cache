import functools
import time
import boto3

def ssm_cache(parameter, ttl_seconds=60, var_name=False):
    """
    Get_parameter in SSM parameter store, and injects it into the event object of the lambda function
    stores the value and timestamp of the get_parameter call into a global map called global_aws_lambda_cache
        if last lookup time was < ttl_seconds ago, value in global map is returned instead
        if last lookup time was >= ttl_seconds ago, get_parameter is called again, repopulating global_aws_lambda_cache
    
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

            parameter_name = get_parameter_name(parameter, var_name)
            parameter_age = get_parameter_age(parameter_name)

            if parameter_age is None:
                event[parameter_name] = get_parameter_from_ssm(parameter, parameter_name)
            elif parameter_age < ttl_seconds:
                event[parameter_name] = get_parameter_from_cache(parameter_name)
            else:
                event[parameter_name] = get_parameter_from_ssm(parameter, parameter_name)

            return func(event, context)
        return inner_function

    return decorator


def get_parameter_name(parameter, var_name):
    """
    Parameter names can include only the following symbols and letters: a-zA-Z0-9_.-/
    if no var_name is specified, we substitute the slash '/' character with underscore '_'.

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
        var_name(string) : Optional name of parameter to inject into event object
    Returns:
        parameter_name   : Name of parameter stored in global_aws_lambda_cache map
    """
    
    if var_name:
        parameter_name = var_name
    else:
        parameter_name = parameter.replace('/', '_')
    
    return parameter_name

def get_parameter_age(parameter_name):
    """
    Args:
        parameter_name(string): Name of parameter to get age for
    
    returns:
        parameter_age_seconds(int): Age of parameter in seconds
    """
    global global_aws_lambda_cache

    try:
        get_param_timestamp = global_aws_lambda_cache[parameter_name]['get_param_timestamp']
        parameter_age = int(time.time() - get_param_timestamp)
    except NameError:  # create global_aws_lambda_cache
        global_aws_lambda_cache = {parameter_name: {'value': None, 'get_param_timestamp': None}}
        parameter_age = None
    except KeyError: # parameter doesn't exist in global_aws_lambda_cache
        global_aws_lambda_cache[parameter_name] = {'value': None, 'get_param_timestamp': None}
        parameter_age = None

    return parameter_age

def get_parameter_from_ssm(parameter, parameter_name):
    """
    Gets parameter value from the System manager Parameter store

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
    Returns:
        parameter_value (string): Value of parameter in Parameter Store
    """

    ssm_client = boto3.client('ssm')
    response = ssm_client.get_parameter(
        Name=parameter,
        WithDecryption=True
    )
    parameter_value = response['Parameter']['Value']

    global global_aws_lambda_cache
    global_aws_lambda_cache[parameter_name] = {'value': parameter_value,
                                               'get_param_timestamp': time.time()}

    return parameter_value

def get_parameter_from_cache(parameter_name):
    """
    Gets parameter value from the System manager Parameter cache

    Args:
        parameter(string): Name of the parameter in System Manager Parameter Store
    Returns:
        parameter_value (string): Value of parameter in Parameter Store
    """

    global global_aws_lambda_cache
    parameter_value = global_aws_lambda_cache.get(parameter_name).get('value')
    return parameter_value

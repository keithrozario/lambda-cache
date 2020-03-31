import time


def check_cache(parameter, ttl_seconds, entry_name, miss_function):
    """
    Executes the caching logic, checks cache for entry
    If entry doesn't exist, returns entry_value by calling the miss function with entry_name and var_name
    If entry does exist check entry_age:
        If entry_age < ttl_seconds, returns value from cache
        If entry_age >= ttl_seconds, returns value by calling miss_function

    Args:
        parameter(string): Name of the parameter ()
        ttl_seconds(int) : Time to Live of the entry in seconds
        entry_name(string) : Optional name of entry in cache, and variable injected into event object
        miss_function(function): Function to execute when there is a miss on the cache
    Returns:
        entry_value(dict)  : {entry_name: entry_value}
    """

    entry_name = get_entry_name(parameter, entry_name)
    entry_age = get_entry_age(entry_name)

    if entry_age is None:
        entry_value = miss_function(parameter)
        update_cache(entry_name, entry_value)
    elif entry_age < ttl_seconds:
        entry_value = get_entry_from_cache(entry_name)
    else:
        entry_value = miss_function(parameter)
        update_cache(entry_name, entry_value)

    return {entry_name: entry_value}


def get_entry_name(parameter, entry_name):
    """
    Parameter is either SSM Parameter, Secret in Secrets Manager or Key in S3 bucket:
        SSM Parameter names can include only the following symbols and letters: a-zA-Z0-9_.-/
        Secret name must be ASCII letters, digits, or the following characters : /_+=.@-
        S3 Keys can have a varied characters

    if entry_name is set, we return entry_name
    if entry_name is False, we default entry_name to the string after the last '/' in parameter

    Args:
        parameter(string)  : Name of the parameter
        entry_name(string) : Optional name of entry in cache, and variable injected into event object
    Returns:
        cache_entry_name   : Name of Entry in the cache
    """

    if entry_name:
        cache_entry_name = entry_name
    else:
        cache_entry_name = parameter.split("/")[-1]

    return cache_entry_name


def get_entry_age(entry_name):
    """
    Args:
        entry_name(string): Name of entry to get age for
    
    returns:
        entry_age_seconds(int): Age of entry in seconds
    """
    global global_aws_lambda_cache

    try:
        get_param_timestamp = global_aws_lambda_cache[entry_name][
            "last_updated_timestamp"
        ]
        entry_age = int(time.time() - get_param_timestamp)

    # cache doesn't exist. Create it.
    except NameError:
        global_aws_lambda_cache = {
            entry_name: {"value": None, "last_updated_timestamp": None}
        }
        entry_age = None

    # entry doesn't exist in cache or is still None (due to partial failure)
    except (KeyError, TypeError):
        global_aws_lambda_cache[entry_name] = {
            "value": None,
            "last_updated_timestamp": None,
        }
        entry_age = None

    return entry_age


def update_cache(entry_name, entry_value):
    global global_aws_lambda_cache

    global_aws_lambda_cache[entry_name] = {
        "value": entry_value,
        "last_updated_timestamp": time.time(),
    }

    return


def get_entry_from_cache(entry_name):
    """
    Gets entry value from the cache

    Args:
        entry_name (string): Name of the entry in cache
    Returns:
        entry_value   (any): Value of entry in cache
    """

    global global_aws_lambda_cache
    entry_value = global_aws_lambda_cache.get(entry_name).get("value")
    return entry_value
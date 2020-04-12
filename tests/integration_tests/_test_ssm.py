import json
from lambda_cache import ssm

# this file is packaged in the lambda using serverless.yml
from variables_data import *


def generic_return(message):
    body = {
        "message": message
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


@ssm.cache(ssm_parameter, max_age_in_seconds=5)
def single_parameter(event, context):
    message = getattr(context, ssm_parameter.split('/')[-1])
    return generic_return(message)

@ssm.cache(ssm_parameter_2, max_age_in_seconds=5, entry_name='default_param')
def rename_param(event, context):
    message = getattr(context, 'default_param')
    return generic_return(message)

@ssm.cache(secure_parameter)
def secure_string(event, context):
    message = getattr(context, secure_parameter.split('/')[-1])
    return generic_return(message)

@ssm.cache(string_list_parameter, max_age_in_seconds=5)
def string_list(event, context):
    message = getattr(context, string_list_parameter.split('/')[-1])
    return generic_return(message)

@ssm.cache(secure_parameter)
@ssm.cache(string_list_parameter, max_age_in_seconds=10)
@ssm.cache(ssm_parameter, max_age_in_seconds=10)
@ssm.cache(ssm_parameter_2, max_age_in_seconds=10)
def multi_parameter(event, context):
    message = {"param_1": getattr(context,ssm_parameter_default_name),
               "param_2": getattr(context,ssm_parameter_2_default_name),
               "param_3": getattr(context,string_list_default_name),
               "param_4": getattr(context,secure_parameter_default_name)}
    return generic_return(message)

@ssm.cache(parameter=[ssm_parameter, ssm_parameter_2, string_list_parameter, secure_parameter], entry_name=default_entry_name, max_age_in_seconds=10)
def multi_parameter_2(event, context):

    cache = getattr(context, default_entry_name)

    message = {"param_1": cache.get(ssm_parameter_default_name),
               "param_2": cache.get(ssm_parameter_2_default_name),
               "param_3": cache.get(string_list_default_name),
               "param_4": cache.get(secure_parameter_default_name)}
    return generic_return(message)


def assign_parameter(event, context):
    message = {"param_1": ssm.get_entry(parameter=ssm_parameter, max_age_in_seconds=20),
               "param_2": ssm.get_entry(parameter=ssm_parameter_2, max_age_in_seconds=30),
               "param_3": ssm.get_entry(parameter=string_list_parameter, max_age_in_seconds=40),
               "param_4": ssm.get_entry(parameter=secure_parameter)}
    return generic_return(message)
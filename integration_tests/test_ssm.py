import json
from aws_lambda_cache import ssm_cache, get_ssm_cache

# this file is packaged in the lambda using serverless.yml
from tests.variables_data import *


def generic_return(message):
    body = {
        "message": message
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


@ssm_cache(ssm_parameter, ttl_seconds=2)
def single_parameter(event, context):
    return generic_return(event.get(ssm_parameter.split('/')[-1]))

@ssm_cache(ssm_parameter_2, ttl_seconds=5, var_name='default_param')
def rename_param(event, context):
    return generic_return(event.get('default_param'))

@ssm_cache(secure_parameter)
def secure_string(event, context):
    return generic_return(event.get(secure_parameter.split('/')[-1]))

@ssm_cache(string_list_parameter, ttl_seconds=2)
def string_list(event, context):
    return generic_return(event.get(string_list_parameter.split('/')[-1]))

@ssm_cache(secure_parameter)
@ssm_cache(string_list_parameter, ttl_seconds=2)
@ssm_cache(ssm_parameter, ttl_seconds=2)
@ssm_cache(ssm_parameter_2, ttl_seconds=2)
def multi_parameter(event, context):
    message = {"param_1": event.get(ssm_parameter_default_name),
               "param_2": event.get(ssm_parameter_2_default_name),
               "param_3": event.get(string_list_default_name),
               "param_4": event.get(secure_parameter_default_name)}
    return generic_return(message)

def assign_parameter(event, context):

    return generic_return(event.get(ssm_parameter.split('/')[-1]))



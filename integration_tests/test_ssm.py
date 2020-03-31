import json
from aws_lambda_cache import ssm_cache

ssm_parameter_name = '/lambda_cache/ssm_parameter'
ssm_parameter_default_name = 'ssm_parameter'
ssm_parameter_name_2 = '/lambda_cache/ssm_parameter_2'
ssm_parameter_default_name_2 = 'ssm_parameter_2'

@ssm_cache(ssm_parameter_name
def single_parameter(event, context):
    
    body = {
        "message": event.get(ssm_parameter_default_name)
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

@ssm_cache(ssm_parameter_name_2)
@ssm_cache(ssm_parameter_name)
def double_parameter(event, context):
    
    body = {
        "message": event.get(ssm_parameter_default_name)
        "message_2": event.get(ssm_parameter_name_2)
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

@ssm_cache(ssm_parameter_name_2, ttl_seconds=5, var_name='default_param')
def rename_param(event, context):
    
    body = {
        "message_2": event.get('default_param')
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

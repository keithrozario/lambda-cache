import json
from aws_lambda_cache import ssm_cache

@ssm_cache('/lambda_cache/ssm_parameter')
def single_parameter(event, context):
    
    body = {
        "message": event.get('_lambda_cache_ssm_parameter')
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

@ssm_cache('/lambda_cache/ssm_parameter_2')
@ssm_cache('/lambda_cache/ssm_parameter')
def double_parameter(event, context):
    
    body = {
        "message": event.get('_lambda_cache_ssm_parameter')
        "message_2": event.get('_lambda_cache_ssm_parameter_2')
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


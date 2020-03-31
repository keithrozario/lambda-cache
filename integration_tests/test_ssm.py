import json
from aws_lambda_cache import ssm_cache

ssm_parameter = "/lambda_cache/something"
ssm_parameter_default_name = "something"
ssm_parameter_2 = "/lambda_cache/test/something_else"
ssm_parameter_2_default_name = "something_else"

@ssm_cache(ssm_parameter, ttl_seconds=2)
def single_parameter(event, context):
    
    body = {
        "message": event.get(ssm_parameter_default_name)
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

@ssm_cache(ssm_parameter, ttl_seconds=2)
@ssm_cache(ssm_parameter_2, ttl_seconds=2)
def double_parameter(event, context):
    
    body = {
        "message": {"param_1": event.get(ssm_parameter_default_name),
                    "param_2": event.get(ssm_parameter_2_default_name)}
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

@ssm_cache(ssm_parameter_2, ttl_seconds=5, var_name='default_param')
def rename_param(event, context):
    
    body = {
        "message": event.get('default_param')
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

import json
import boto3

from lambda_cache import ssm
from datetime import datetime

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

@ssm.cache(parameter=[ssm_parameter, ssm_parameter_2, string_list_parameter, secure_parameter], entry_name=default_entry_name, max_age_in_seconds=10)
def multi_parameter_2(event, context):

    cache = getattr(context, default_entry_name)

    message = {"param_1": cache.get(ssm_parameter_default_name),
               "param_2": cache.get(ssm_parameter_2_default_name),
               "param_3": cache.get(string_list_default_name),
               "param_4": cache.get(secure_parameter_default_name)}

    client = boto3.client('ssm')
    response = client.put_parameter(
        Name=ssm_parameter,
        Value=datetime.now().isoformat(),
        Type='String',
        Overwrite=True)

    return generic_return(message)
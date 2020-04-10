import json
from lambda_cache import secrets_manager

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


@secrets_manager.cache(name=secret_name_string, max_age_in_seconds=5)
def secret_string(event, context):
    message = getattr(context, secret_name_string.split('/')[-1])
    return generic_return(message)

@secrets_manager.cache(name=secret_name_binary, max_age_in_seconds=5)
def secret_binary(event, context):
    message = getattr(context, secret_name_binary.split('/')[-1])
    return generic_return(message.decode('utf-8'))

@secrets_manager.cache(name=secret_name_string)
def secret_string_default(event, context):
    message = getattr(context, secret_name_string.split('/')[-1])
    return generic_return(message)
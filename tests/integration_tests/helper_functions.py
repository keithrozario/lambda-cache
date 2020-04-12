import boto3
import yaml
import json


def get_message_from_lambda(function_name):

    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        LogType='None'
    )

    result = json.loads((response.get('Payload').read()).decode('utf-8'))
    return json.loads(result['body'])['message']


def get_serverless_config():
    with open('serverless.yml', 'r') as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    
    return config
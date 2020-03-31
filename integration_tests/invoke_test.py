import boto3
import yaml
import json
import time


def get_message_from_lambda():

    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        LogType='None'
    )

    result = json.loads((response.get('Payload').read()).decode('utf-8'))
    print(json.loads(result['body'])['message'])


def put_parameter(value):

    ssm_client = boto3.client('ssm')
    response = ssm_client.put_parameter(
        Name=config.get('custom').get('parameter_name'),
        Value=value,
        Type='String',
        Overwrite=True
    )
    return response


with open('serverless.yml', 'r') as config_file:
    config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
service = config['service']
stage = config['provider']['stage']
function_name = f"{service}-{stage}-test_ssm"

get_message_from_lambda()
put_parameter('DUMMY NEW')
get_message_from_lambda()
time.sleep(2)
get_message_from_lambda()
put_parameter('DUMMY NEW NEW!!')
get_message_from_lambda()
time.sleep(2)
get_message_from_lambda()
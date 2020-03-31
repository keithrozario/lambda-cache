import boto3
import yaml
import json
import time

from tests.helper_functions import update_parameter
from tests.variables_data import *

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
    with open('../integration_tests/serverless.yml', 'r') as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    
    return config

def initialize():
    update_parameter(ssm_parameter, ssm_parameter_value)
    update_parameter(ssm_parameter_2, ssm_parameter_2_value)
    update_parameter(secure_parameter, secure_parameter_value, param_type='SecureString')
    update_parameter(string_list_parameter,string_list_value, param_type='StringList')

def test_lambda_single_hander():
    initialize()
    function_name = f"{service}-{stage}-single_handler"

    new_value = "NEW VALUE!!!"

    value = get_message_from_lambda(function_name)
    assert value == ssm_parameter_value
    
    update_parameter(ssm_parameter, new_value)
    value = get_message_from_lambda(function_name)
    assert value == ssm_parameter_value
    
    time.sleep(2)
    value = get_message_from_lambda(function_name)
    assert value == new_value

    update_parameter(ssm_parameter, ssm_parameter_value)
    value = get_message_from_lambda(function_name)
    assert value == new_value

    time.sleep(2)
    value = get_message_from_lambda(function_name)
    assert value == ssm_parameter_value

def test_lambda_double_handler():
    initialize()
    function_name = f"{service}-{stage}-double_handler"
    new_value = "NEW VALUE!!!"

    value = get_message_from_lambda(function_name)
    assert value == {"param_1": ssm_parameter_value, "param_2": ssm_parameter_2_value}
    
    update_parameter(ssm_parameter_2, new_value)
    value = get_message_from_lambda(function_name)
    assert value == {"param_1": ssm_parameter_value, "param_2": ssm_parameter_2_value}

    time.sleep(2)
    value = get_message_from_lambda(function_name)
    assert value == {"param_1": ssm_parameter_value, "param_2":  new_value}


def test_renamed_var():
    initialize()
    function_name = f"{service}-{stage}-default_param"
    new_value = "NEW VALUE!!!"

    value = get_message_from_lambda(function_name)
    assert value == ssm_parameter_2_value

    update_parameter(ssm_parameter_2, new_value)
    value = get_message_from_lambda(function_name)
    assert value == ssm_parameter_2_value

    value = get_message_from_lambda(function_name)
    assert value == ssm_parameter_2_value

    time.sleep(5)
    value = get_message_from_lambda(function_name)
    assert value == new_value


config = get_serverless_config()
service = config['service']
stage = config['provider']['stage']
import boto3
import yaml
import json
import time
import random
import string

from tests.helper_functions import update_parameter, delete_parameters
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

def generic_test(function_name,parameter_name,parameter_value,sleep_time=60, param_type='String'):
    new_value = ''.join(random.choices(string.ascii_lowercase, k = 8))

    value = get_message_from_lambda(function_name)
    assert value == parameter_value

    update_parameter(parameter_name, new_value, param_type)
    value = get_message_from_lambda(function_name)
    assert value == parameter_value

    time.sleep(sleep_time)
    value = get_message_from_lambda(function_name)
    assert value == new_value

    update_parameter(parameter_name, parameter_value, param_type)
    value = get_message_from_lambda(function_name)
    assert value == new_value

    time.sleep(sleep_time)
    value = get_message_from_lambda(function_name)
    assert value == parameter_value

def test_initialize():
    delete_parameters([ssm_parameter, ssm_parameter_2, secure_parameter, string_list_parameter])
    update_parameter(ssm_parameter, ssm_parameter_value)
    update_parameter(ssm_parameter_2, ssm_parameter_2_value)
    update_parameter(secure_parameter, secure_parameter_value, param_type='SecureString')
    update_parameter(string_list_parameter,string_list_value, param_type='StringList')

def test_lambda_single_hander():
    function_name = f"{service}-{stage}-single_handler"
    generic_test(function_name, ssm_parameter,ssm_parameter_value, 2)

def test_renamed_var():
    function_name = f"{service}-{stage}-default_param"
    generic_test(function_name, ssm_parameter_2, ssm_parameter_2_value, 5, param_type='StringList')

def test_secure_string():
    function_name = f"{service}-{stage}-secure_string"
    generic_test(function_name, secure_parameter, secure_parameter_value, param_type='SecureString')

def test_lambda_multi_handler():
    function_name = f"{service}-{stage}-multi_handler"
    return_value = {"param_1": ssm_parameter_value, 
                    "param_2": ssm_parameter_2_value,
                    "param_3": string_list_value.split(','),
                    "param_4": secure_parameter_value}
    
    new_value = ''.join(random.choices(string.ascii_lowercase, k = 8))

    value = get_message_from_lambda(function_name)
    assert value == return_value
    
    update_parameter(ssm_parameter, new_value)
    update_parameter(ssm_parameter_2, new_value)
    value = get_message_from_lambda(function_name)
    assert value == return_value

    time.sleep(2)
    value = get_message_from_lambda(function_name)
    return_value["param_1"] = new_value
    return_value["param_2"] = new_value
    assert value == return_value

def test_lambda_assign_parameter():
    test_initialize()
    function_name = f"{service}-{stage}-assign_parameter"
    return_value = {"param_1": ssm_parameter_value, 
                    "param_2": ssm_parameter_2_value,
                    "param_3": string_list_value.split(','),
                    "param_4": secure_parameter_value}
    
    new_value = ''.join(random.choices(string.ascii_lowercase, k = 8))
    
    value = get_message_from_lambda(function_name)
    assert value == return_value

    update_parameter(ssm_parameter, new_value)
    update_parameter(ssm_parameter_2, new_value)
    update_parameter(secure_parameter, new_value)
    value = get_message_from_lambda(function_name)
    assert value == return_value

    time.sleep(20) # after 20 seconds
    return_value['param_1'] = new_value
    value = get_message_from_lambda(function_name)
    assert value == return_value

    time.sleep(10) # after 30 seconds
    return_value['param_2'] = new_value
    value = get_message_from_lambda(function_name)
    assert value == return_value

    time.sleep(30) # after 60 seconds
    return_value['param_4'] = new_value
    value = get_message_from_lambda(function_name)
    assert value == return_value
    


# Config Variables
config = get_serverless_config()
service = config['service']
stage = config['provider']['stage']


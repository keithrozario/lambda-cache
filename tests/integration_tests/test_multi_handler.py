import random
import string
import time

from tests.integration_tests.test_deployed_lambda import test_initialize
from tests.variables_data import *
from tests.helper_functions import update_parameter, delete_parameters
from tests.integration_tests.helper_functions import get_serverless_config, get_message_from_lambda

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

    time.sleep(10)
    value = get_message_from_lambda(function_name)
    return_value["param_1"] = new_value
    return_value["param_2"] = new_value
    assert value == return_value

# Config Variables
config = get_serverless_config()
service = config['service']
stage = config['provider']['stage']
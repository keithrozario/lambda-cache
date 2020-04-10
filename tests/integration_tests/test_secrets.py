import time
import random
import string

from tests.variables_data import *
from tests.helper_functions import update_secret

from tests.integration_tests.helper_functions import get_message_from_lambda, get_serverless_config

def generic_test(function_name, secret_name,  secret_value, sleep_time=60, secret_type='String'):
    
    dummy_value = ''.join(random.choices(string.ascii_lowercase, k = 25))
    dummy_value_returned = dummy_value
    if secret_type == 'Binary':
        secret_value = secret_value.decode('utf-8')
        dummy_value = dummy_value.encode('utf-8')

    value = get_message_from_lambda(function_name)
    assert value == secret_value

    update_secret(secret_name, dummy_value, secret_type)
    value = get_message_from_lambda(function_name)
    assert value == secret_value

    time.sleep(sleep_time)
    value = get_message_from_lambda(function_name)
    assert value == dummy_value_returned

    update_secret(secret_name, secret_value, secret_type)
    value = get_message_from_lambda(function_name)
    assert value == dummy_value_returned

    time.sleep(sleep_time)
    value = get_message_from_lambda(function_name)
    assert value == secret_value

def test_initialize():
    update_secret(secret_name_string, secret_name_string_value, secret_type='String')
    update_secret(secret_name_binary, secret_name_binary_value, secret_type='Binary')

def test_lambda_secret_string():
    function_name = f"{service}-{stage}-secret_string"
    generic_test(function_name, secret_name_string ,secret_name_string_value, 5)

def test_lambda_secret_binary():
    function_name = f"{service}-{stage}-secret_binary"
    generic_test(function_name, secret_name_binary ,secret_name_binary_value, 5, secret_type='Binary')

def test_lambda_default():
    function_name = f"{service}-{stage}-secret_string_default"
    generic_test(function_name, secret_name_string ,secret_name_string_value, 60)


# Config Variables
config = get_serverless_config()
service = config['service']
stage = config['provider']['stage']
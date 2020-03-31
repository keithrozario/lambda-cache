from aws_lambda_cache import __version__
from aws_lambda_cache import ssm_cache
from aws_lambda_cache import get_ssm_cache

import time
import random, string
import pytest
from botocore.exceptions import ClientError

from tests.variables_data import *
from tests.helper_functions import update_parameter


def test_initialize():
    assert __version__ == '0.2.5'
    update_parameter(ssm_parameter, ssm_parameter_value)
    update_parameter(ssm_parameter_2, ssm_parameter_2_value)
    update_parameter(secure_parameter, secure_parameter_value, param_type='SecureString')
    update_parameter(long_name_parameter, long_name_value)
    update_parameter(string_list_parameter,string_list_value, param_type='StringList')

# Test parameter assignment
def test_get_parameter():

    parameter_assignment(ssm_parameter, ssm_parameter_value)
    parameter_assignment(secure_parameter, secure_parameter_value, 'SecureString')
    parameter_assignment(string_list_parameter, string_list_value, parameter_type='StringList')


def parameter_assignment(parameter, parameter_value, parameter_type='String'):

    dummy_name = ''.join(random.choices(string.ascii_lowercase, k = 8)) 
    
    if parameter_type == 'StringList':
        dummy_value = "d,e,f"
        dummy_value_return = dummy_value.split(",")
        parameter_value_return = parameter_value.split(",")
    else:
        dummy_value = 'get_dummy'
        dummy_value_return = dummy_value
        parameter_value_return = parameter_value

    ttl = 2

    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl, var_name=dummy_name)
    assert param == parameter_value_return
    
    update_parameter(parameter, dummy_value, parameter_type)
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl, var_name=dummy_name)
    assert param == parameter_value_return

    time.sleep(ttl)
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl, var_name=dummy_name)
    assert param == dummy_value_return
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl, var_name=dummy_name)
    assert param == dummy_value_return

    time.sleep(ttl)
    update_parameter(parameter, parameter_value, parameter_type)
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl, var_name=dummy_name)
    assert param == parameter_value_return

# Test Non-existent parameter

@ssm_cache(parameter="/some/nonexist/parameter")
def parameter_not_exist_var_handler(event, context):
    return event

def test_non_existing_parameter():
    
    test_event = {'event_name': 'test'}
    test_context = {}
    with pytest.raises(ClientError) as e:
        event = parameter_not_exist_var_handler(test_event, test_context)
        assert e['Error']['Code'] == "ParameterNotFound"


# Test parameter import and stacking
@ssm_cache(parameter=ssm_parameter)
def single_var_handler(event, context):
    return event

@ssm_cache(parameter=ssm_parameter)
@ssm_cache(parameter=ssm_parameter_2)
def double_var_handler(event, context):
    return event


@ssm_cache(parameter=long_name_parameter)
def long_name_var_handler(event,context):
    return event

def test_var_handlers():

    test_event = {'event_name': 'test'}
    test_context = {}

    event = single_var_handler(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value
    
    event = double_var_handler(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value
    assert event.get(ssm_parameter_2_default_name) == ssm_parameter_2_value

    event = long_name_var_handler(test_event, test_context)
    assert event.get(long_name_default_name) == long_name_value


# Test Parameter Caching TTL settings
@ssm_cache(parameter=ssm_parameter, ttl_seconds=5)
def five_second_ttl(event, context):
    return event

def test_cache():
    
    updated_value = 'Dummy Value NEW!!'

    test_event = {'event_name': 'test'}
    test_context = {}

    event = five_second_ttl(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value
    
    # Update parameter but call before 5 seconds
    update_parameter(ssm_parameter, updated_value)
    event = five_second_ttl(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value

    # Wait 5 seconds call again
    time.sleep(5)
    event = five_second_ttl(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == updated_value

    # Revert back to normal
    update_parameter(ssm_parameter, ssm_parameter_value)
    time.sleep(5)
    event = five_second_ttl(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value

# Test Parameter Rename
@ssm_cache(parameter=ssm_parameter, var_name=ssm_parameter_replaced_var_name)
def renamed_var(event, context):
    return event

def test_rename_parameter():

    test_event = {'event_name': 'test'}
    test_context = {}

    event = renamed_var(test_event, test_context)
    assert event.get(ssm_parameter_replaced_var_name) == ssm_parameter_value

# Test Secure String import
@ssm_cache(parameter=secure_parameter)
def secure_var_handler(event,context):
    return event

def test_secure_string():

    test_event = {'event_name': 'test'}
    test_context = {}

    event = secure_var_handler(test_event, test_context)
    assert event.get(secure_parameter_default_name) == secure_parameter_value

# Test ttl_seconds=0 settings, no cache
@ssm_cache(parameter=ssm_parameter, ttl_seconds=0)
def no_cache(event, context):
    return event

def test_no_cache():
    test_event = {'event_name': 'test'}
    test_context = {}
    new_value = "New Value"

    event = no_cache(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value
    
    update_parameter(ssm_parameter, new_value)
    event = no_cache(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == new_value

    update_parameter(ssm_parameter, ssm_parameter_value)
    event = no_cache(test_event, test_context)
    assert event.get(ssm_parameter_default_name) == ssm_parameter_value

# Test StringList with cache
@ssm_cache(parameter=string_list_parameter, ttl_seconds=2)
def string_list(event, context):
    return event



def test_string_list():
    dummy_value = 'd,e,f'
    dummy_value_return = dummy_value.split(',')

    
    return_list = string_list({},{}).get(string_list_default_name)
    assert return_list == string_list_value.split(',')
    
    update_parameter(string_list_parameter,dummy_value,param_type='StringList')
    time.sleep(1)
    return_list = string_list({},{}).get(string_list_default_name)
    assert return_list == string_list_value.split(',')

    time.sleep(1)
    return_list = string_list({},{}).get(string_list_default_name)
    assert return_list == dummy_value_return

    update_parameter(string_list_parameter,string_list_value, param_type='StringList')
    time.sleep(2)
    return_list = string_list({},{}).get(string_list_default_name)
    assert return_list == string_list_value.split(',')
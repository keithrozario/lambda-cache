from simple_lambda_cache import __version__
from simple_lambda_cache import ssm_cache
from simple_lambda_cache import get_ssm_cache
from simple_lambda_cache.exceptions import ArgumentTypeNotSupportedError, NoEntryNameError

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

    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl)
    assert param == parameter_value_return
    
    update_parameter(parameter, dummy_value, parameter_type)
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl)
    assert param == parameter_value_return

    time.sleep(ttl)
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl)
    assert param == dummy_value_return
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl)
    assert param == dummy_value_return

    time.sleep(ttl)
    update_parameter(parameter, parameter_value, parameter_type)
    param = get_ssm_cache(parameter=parameter, ttl_seconds=ttl)
    assert param == parameter_value_return

# Test Non-existent parameter

@ssm_cache(parameter="/some/nonexist/parameter")
def parameter_not_exist_var_handler(event, context):
    return context

def test_non_existing_parameter():
    
    test_event = {'event_name': 'test'}
    test_context = {}
    with pytest.raises(ClientError) as e:
        context = parameter_not_exist_var_handler(test_event, test_context)
        assert e['Error']['Code'] == "ParameterNotFound"


# Test parameter import and stacking
@ssm_cache(parameter=ssm_parameter)
def single_var_handler(event, context):
    return context

@ssm_cache(parameter=ssm_parameter)
@ssm_cache(parameter=ssm_parameter_2)
def double_var_handler(event, context):
    return context


@ssm_cache(parameter=long_name_parameter)
def long_name_var_handler(event,context):
    return context

def test_var_handlers():

    test_event = {'event_name': 'test'}
    test_context = {}

    context = single_var_handler(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value
    
    context = double_var_handler(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value
    assert context.get(ssm_parameter_2_default_name) == ssm_parameter_2_value

    context = long_name_var_handler(test_event, test_context)
    assert context.get(long_name_default_name) == long_name_value


# Test Parameter Caching TTL settings
@ssm_cache(parameter=ssm_parameter, ttl_seconds=5)
def five_second_ttl(event, context):
    return context

def test_cache():
    
    updated_value = 'Dummy Value NEW!!'

    test_event = {'event_name': 'test'}
    test_context = {}

    context = five_second_ttl(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value
    
    # Update parameter but call before 5 seconds
    update_parameter(ssm_parameter, updated_value)
    context = five_second_ttl(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value

    # Wait 5 seconds call again
    time.sleep(5)
    context = five_second_ttl(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == updated_value

    # Revert back to normal
    update_parameter(ssm_parameter, ssm_parameter_value)
    time.sleep(5)
    context = five_second_ttl(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value

# Test Parameter Rename
@ssm_cache(parameter=ssm_parameter, entry_name=ssm_parameter_replaced_var_name)
def renamed_var(event, context):
    return context

def test_rename_parameter():

    test_event = {'event_name': 'test'}
    test_context = {}

    context = renamed_var(test_event, test_context)
    assert context.get(ssm_parameter_replaced_var_name) == ssm_parameter_value

# Test Secure String import
@ssm_cache(parameter=secure_parameter)
def secure_var_handler(event,context):
    return context

def test_secure_string():

    test_event = {'event_name': 'test'}
    test_context = {}

    context = secure_var_handler(test_event, test_context)
    assert context.get(secure_parameter_default_name) == secure_parameter_value

# Test ttl_seconds=0 settings, no cache
@ssm_cache(parameter=ssm_parameter, ttl_seconds=0)
def no_cache(event, context):
    return context

def test_no_cache():
    test_event = {'event_name': 'test'}
    test_context = {}
    new_value = "New Value"

    context = no_cache(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value
    
    update_parameter(ssm_parameter, new_value)
    context = no_cache(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == new_value

    update_parameter(ssm_parameter, ssm_parameter_value)
    context = no_cache(test_event, test_context)
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value

# Test StringList with cache
@ssm_cache(parameter=string_list_parameter, ttl_seconds=2)
def string_list(event, context):
    return context


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

# Test invalid parameter
@ssm_cache(parameter=123, entry_name="hello")
def invalid_parameter(event, context):
    return context

def test_invalid_parameter():

    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        returned_value = invalid_parameter({}, {})
        assert e['Code'] == "ArgumentTypeNotSupportedError"

    with pytest.raises(NoEntryNameError) as e:
        get_ssm_cache(parameter=123, ttl_seconds=4)
        assert e['Code'] == "NoEntryNameError"
    
    with pytest.raises(NoEntryNameError) as e:
        get_ssm_cache(parameter={'dummy': 'dict'}, ttl_seconds=2)
        assert e['Code'] == "NoEntryNameError"
    
    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        get_ssm_cache(parameter=123, ttl_seconds=2, entry_name="hello")
        assert e['Code'] == "ArgumentTypeNotSupportedError"

    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        get_ssm_cache(parameter=(123,123), ttl_seconds=2, entry_name="hello")
        assert e['Code'] == "ArgumentTypeNotSupportedError"
    
    with pytest.raises(NoEntryNameError) as e:
        get_ssm_cache(parameter=['abc','_'], ttl_seconds=2)
        assert e['Code'] == "NoEntryNameError"

# Test get_parameters
@ssm_cache(parameter=[ssm_parameter, ssm_parameter_2, string_list_parameter, secure_parameter], entry_name=default_entry_name, ttl_seconds=10)
def multi_parameters(event, context):
    return context

def test_multi_parameters():

    dummy_string = "__"
    dummy_list = "-,--,---"

    context = multi_parameters({},{})
    assert context.get(default_entry_name).get(ssm_parameter_default_name) == ssm_parameter_value
    assert context.get(default_entry_name).get(ssm_parameter_2_default_name) == ssm_parameter_2_value
    assert context.get(default_entry_name).get(string_list_default_name) == string_list_value.split(',')
    assert context.get(default_entry_name).get(secure_parameter_default_name) == secure_parameter_value

    update_parameter(ssm_parameter, dummy_string)
    update_parameter(ssm_parameter_2, dummy_string)
    update_parameter(secure_parameter, dummy_string, param_type='SecureString')
    update_parameter(string_list_parameter, dummy_list, param_type='StringList')
    context = multi_parameters({},{})
    assert context.get(default_entry_name).get(ssm_parameter_default_name) == ssm_parameter_value
    assert context.get(default_entry_name).get(ssm_parameter_2_default_name) == ssm_parameter_2_value
    assert context.get(default_entry_name).get(string_list_default_name) == string_list_value.split(',')
    assert context.get(default_entry_name).get(secure_parameter_default_name) == secure_parameter_value

    time.sleep(10)
    context = multi_parameters({},{})
    assert context.get(default_entry_name).get(ssm_parameter_default_name) == dummy_string
    assert context.get(default_entry_name).get(ssm_parameter_2_default_name) == dummy_string
    assert context.get(default_entry_name).get(string_list_default_name) == dummy_list.split(',')
    assert context.get(default_entry_name).get(secure_parameter_default_name) == dummy_string

    test_initialize()
    context = multi_parameters({},{})
    assert context.get(default_entry_name).get(ssm_parameter_default_name) == dummy_string
    assert context.get(default_entry_name).get(ssm_parameter_2_default_name) == dummy_string
    assert context.get(default_entry_name).get(string_list_default_name) == dummy_list.split(',')
    assert context.get(default_entry_name).get(secure_parameter_default_name) == dummy_string
    
    time.sleep(10)
    context = multi_parameters({},{})
    assert context.get(default_entry_name).get(ssm_parameter_default_name) == ssm_parameter_value
    assert context.get(default_entry_name).get(ssm_parameter_2_default_name) == ssm_parameter_2_value
    assert context.get(default_entry_name).get(string_list_default_name) == string_list_value.split(',')
    assert context.get(default_entry_name).get(secure_parameter_default_name) == secure_parameter_value

# Test Parameter Caching TTL settings
@ssm_cache(parameter=ssm_parameter, ttl_seconds=10)
def invalidate_cache(event, context):
    if event.get('refresh', False):
        result = get_ssm_cache(ssm_parameter, ttl_seconds=0)
        context[ssm_parameter_default_name] = result
    return context

def test_invalidate_cache():
    
    updated_value = 'Dummy Value NEW!!'

    refresh_event = {'refresh': True}

    context = invalidate_cache({}, {})
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value
    
    # Update parameter and test within 5 seconds
    update_parameter(ssm_parameter, updated_value)
    time.sleep(5)
    context = invalidate_cache({}, {})
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value

    # Wait 5 seconds call again, parameter should be refreshed
    time.sleep(5)
    context = invalidate_cache({}, {})
    assert context.get(ssm_parameter_default_name) == updated_value

    # Update parameter back to ssm_parameter_value, but call with invalidated cache
    update_parameter(ssm_parameter, ssm_parameter_value)
    context = invalidate_cache(refresh_event, {})
    assert context.get(ssm_parameter_default_name) == ssm_parameter_value
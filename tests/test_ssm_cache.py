from lambda_cache import ssm
from lambda_cache.exceptions import ArgumentTypeNotSupportedError, NoEntryNameError
from tests.context_object import LambdaContext

import time
import random, string
import pytest
from botocore.exceptions import ClientError
import toml

from tests.variables_data import *
from tests.helper_functions import update_parameter


def test_initialize():
    update_parameter(ssm_parameter, ssm_parameter_value)
    update_parameter(ssm_parameter_2, ssm_parameter_2_value)
    update_parameter(secure_parameter, secure_parameter_value, param_type='SecureString')
    update_parameter(long_name_parameter, long_name_value)
    update_parameter(string_list_parameter,string_list_value, param_type='StringList')

# Test parameter import and stacking
@ssm.cache(parameter=ssm_parameter)
def single_var_handler(event, context):
    return context

@ssm.cache(parameter=ssm_parameter)
@ssm.cache(parameter=ssm_parameter_2)
def double_var_handler(event, context):
    return context

@ssm.cache(parameter=long_name_parameter)
def long_name_var_handler(event,context):
    return context

def test_var_handlers():

    test_event = {'event_name': 'test'}
    test_context = LambdaContext()

    context = single_var_handler(test_event, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value
    
    context = double_var_handler(test_event, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value
    assert getattr(context, ssm_parameter_2_default_name) == ssm_parameter_2_value

    context = long_name_var_handler(test_event, test_context)
    assert getattr(context, long_name_default_name) == long_name_value


# Test Parameter Caching TTL settings
@ssm.cache(parameter=ssm_parameter, max_age_in_seconds=5)
def five_second_ttl(event, context):
    return context

# Test Parameter Rename
@ssm.cache(parameter=ssm_parameter, entry_name=ssm_parameter_replaced_var_name, max_age_in_seconds=5)
def renamed_var(event, context):
    return context

# Test Secure String import
@ssm.cache(parameter=secure_parameter, max_age_in_seconds=5)
def secure_var_handler(event,context):
    return context

# Test StringList with cache
@ssm.cache(parameter=string_list_parameter, max_age_in_seconds=5)
def string_list(event, context):
    return context

def test_decorated_functions():

    decorator_test(five_second_ttl, ssm_parameter, ssm_parameter_default_name, ssm_parameter_value, 5)
    decorator_test(renamed_var, ssm_parameter, ssm_parameter_replaced_var_name, ssm_parameter_value, 5)
    decorator_test(secure_var_handler,secure_parameter, secure_parameter_default_name, secure_parameter_value, 5, param_type='SecureString')
    decorator_test(string_list, string_list_parameter,string_list_default_name, string_list_value.split(','), 5, param_type='StringList')

def decorator_test(decorated_function, parameter_name, entry_name, parameter_value, max_age_in_seconds, param_type='String'):
    
    dummy_value_updated = ''.join(random.choices(string.ascii_lowercase, k = 25))
    dummy_value_returned = dummy_value_updated
    revert_parameter_value = parameter_value
    if param_type == 'StringList':
        dummy_value_updated = ','.join(random.choices(string.ascii_lowercase, k = 5))
        dummy_value_returned = dummy_value_updated.split(',')
        revert_parameter_value = ','.join(parameter_value)
    
    test_event = {'event_name': 'test'}
    test_context = LambdaContext()

    context = decorated_function(test_event, test_context)
    assert getattr(context, entry_name) == parameter_value
    
    # Update parameter but call before max_age_in_seconds
    update_parameter(parameter_name, dummy_value_updated, param_type=param_type)
    context = decorated_function(test_event, test_context)
    assert getattr(context, entry_name) == parameter_value

    # Wait max_age_in_seconds call again
    time.sleep(max_age_in_seconds)
    context = decorated_function(test_event, test_context)
    assert getattr(context, entry_name) == dummy_value_returned

    # Revert back to normal
    update_parameter(parameter_name, revert_parameter_value, param_type=param_type)
    time.sleep(max_age_in_seconds)
    context = decorated_function(test_event, test_context)
    assert getattr(context, entry_name) == parameter_value



# Test Parameter Caching TTL settings
@ssm.cache(parameter=ssm_parameter, max_age_in_seconds=10)
def invalidate_cache(event, context):
    if event.get('refresh', False):
        result = ssm.get_entry(ssm_parameter, max_age_in_seconds=0)
        setattr(context, ssm_parameter_default_name, result)
    return context

def test_invalidate_cache():
    
    updated_value = 'Dummy Value NEW!!'
    test_event = {}
    test_context = LambdaContext()
    refresh_event = {'refresh': True}

    context = invalidate_cache({}, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value
    
    # Update parameter and test within 5 seconds
    update_parameter(ssm_parameter, updated_value)
    time.sleep(5)
    context = invalidate_cache({}, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value

    # Wait 5 seconds call again, parameter should be refreshed
    time.sleep(5)
    context = invalidate_cache({}, test_context)
    assert getattr(context, ssm_parameter_default_name) == updated_value

    # Update parameter back to ssm_parameter_value, but call with invalidated cache
    update_parameter(ssm_parameter, ssm_parameter_value)
    context = invalidate_cache(refresh_event, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value

# Test max_age_in_seconds=0 settings, no cache
@ssm.cache(parameter=ssm_parameter, max_age_in_seconds=0)
def no_cache(event, context):
    return context

def test_no_cache():
    test_event = {'event_name': 'test'}
    test_context = LambdaContext()
    new_value = "New Value"

    context = no_cache(test_event, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value
    
    update_parameter(ssm_parameter, new_value)
    context = no_cache(test_event, test_context)
    assert getattr(context, ssm_parameter_default_name) == new_value

    update_parameter(ssm_parameter, ssm_parameter_value)
    context = no_cache(test_event, test_context)
    assert getattr(context, ssm_parameter_default_name) == ssm_parameter_value
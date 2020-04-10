from lambda_cache import secrets_manager
from lambda_cache.exceptions import ArgumentTypeNotSupportedError, NoEntryNameError
from tests.context_object import LambdaContext

import time
import random, string
import pytest
from botocore.exceptions import ClientError

from tests.variables_data import *
from tests.helper_functions import update_secret

def test_initialize():
    update_secret(secret_name_string, secret_name_string_value)
    update_secret(secret_name_binary, secret_name_binary_value, secret_type='Binary')

def test_get_secrets():

    parameter_assignment(secret_name_string, secret_name_string_value, secret_type='String')
    parameter_assignment(secret_name_binary, secret_name_binary_value, secret_type='Binary')

def test_default_decorators():

    dummy_value = ''.join(random.choices(string.ascii_lowercase, k = 25))
    decorator_test(secret_name_string, secret_string_default_name, secret_name_string_value, normal_call, ttl=60)
    decorator_test(secret_name_string, secret_string_default_name, secret_name_string_value, call_with_ttl, ttl=10)
    decorator_test(secret_name_string, "new_secret", secret_name_string_value, call_with_entry_name, ttl=10)
    decorator_test(secret_name_binary, "binary_secret", secret_name_binary_value, call_binary, ttl=10, secret_type='Binary')

def test_invalid_parameters():
    
    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        secrets_manager.get_entry(name=123, entry_name="dummy")
        assert e['Code'] == "ArgumentTypeNotSupportedError"
    
    with pytest.raises(NoEntryNameError) as e:
        secrets_manager.get_entry(name=123)
        assert e['Code'] == "NoEntryNameError"


# Test parameter assignment
def parameter_assignment(secret_name, secret_value, secret_type='String', ttl=10):

    dummy_value = ''.join(random.choices(string.ascii_lowercase, k = 25))
    if secret_type == 'Binary':
        dummy_value = dummy_value.encode('utf-8')

    secret = secrets_manager.get_entry(name=secret_name, max_age_in_seconds=ttl)
    assert secret == secret_value
    
    # update and check, should be old value
    update_secret(secret_name, dummy_value, secret_type)
    secret = secrets_manager.get_entry(name=secret_name, max_age_in_seconds=ttl)
    assert secret == secret_value

    # Wait ttl, previous update should now appear
    time.sleep(ttl)
    secret = secrets_manager.get_entry(name=secret_name, max_age_in_seconds=ttl)
    assert secret == dummy_value

    # Update back to original number, dummy value should still be present in cache
    update_secret(secret_name, secret_value, secret_type)
    time.sleep(int(ttl/2))
    secret = secrets_manager.get_entry(name=secret_name, max_age_in_seconds=ttl)
    assert secret == dummy_value

    # Update back to original number, dummy value should still be present in cache
    time.sleep(int(ttl/2)+1)
    secret = secrets_manager.get_entry(name=secret_name, max_age_in_seconds=ttl)
    assert secret == secret_value

# Test Parameter Caching TTL settings
@secrets_manager.cache(name=secret_name_string)
def normal_call(event, context):
    return context

@secrets_manager.cache(name=secret_name_string, max_age_in_seconds=10)
def call_with_ttl(event, context):
    return context

@secrets_manager.cache(name=secret_name_string, max_age_in_seconds=10, entry_name="new_secret")
def call_with_entry_name(event, context):
    return context

@secrets_manager.cache(name=secret_name_binary, max_age_in_seconds=10, entry_name="binary_secret")
def call_binary(event, context):
    return context

def decorator_test(name, entry_name, secret_value, decorated_function, ttl=10, secret_type='String'):

    dummy_value = ''.join(random.choices(string.ascii_lowercase, k = 25))
    if secret_type == 'Binary':
        dummy_value = dummy_value.encode('utf-8')
    
    test_event = dict()
    test_context = LambdaContext()

    context = decorated_function(test_event ,test_context)
    assert getattr(context, entry_name) == secret_value
    
    update_secret(name, dummy_value, secret_type=secret_type)
    context = decorated_function(test_event ,test_context)
    assert getattr(context, entry_name) == secret_value
    
    time.sleep(ttl)
    context = decorated_function(test_event ,test_context)
    assert getattr(context, entry_name) == dummy_value

    update_secret(name, secret_value, secret_type=secret_type)
    context = decorated_function(test_event ,test_context)
    assert getattr(context, entry_name) == dummy_value
    
    time.sleep(ttl)
    context = decorated_function(test_event ,test_context)
    assert getattr(context, entry_name) == secret_value
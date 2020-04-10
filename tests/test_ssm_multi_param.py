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
from tests.test_ssm_cache import test_initialize

# Test get_parameters
@ssm.cache(parameter=[ssm_parameter, ssm_parameter_2, string_list_parameter, secure_parameter], entry_name=default_entry_name, max_age_in_seconds=10)
def multi_parameters(event, context):
    return context

def test_multi_parameters():

    dummy_string = "__"
    dummy_list = "-,--,---"
    test_event = {}
    test_context = LambdaContext()

    context = multi_parameters(test_event,test_context)
    assert getattr(context, default_entry_name).get(ssm_parameter_default_name) == ssm_parameter_value
    assert getattr(context, default_entry_name).get(ssm_parameter_2_default_name) == ssm_parameter_2_value
    assert getattr(context, default_entry_name).get(string_list_default_name) == string_list_value.split(',')
    assert getattr(context, default_entry_name).get(secure_parameter_default_name) == secure_parameter_value

    update_parameter(ssm_parameter, dummy_string)
    update_parameter(ssm_parameter_2, dummy_string)
    update_parameter(secure_parameter, dummy_string, param_type='SecureString')
    update_parameter(string_list_parameter, dummy_list, param_type='StringList')
    context = multi_parameters(test_event,test_context)
    assert getattr(context, default_entry_name).get(ssm_parameter_default_name) == ssm_parameter_value
    assert getattr(context, default_entry_name).get(ssm_parameter_2_default_name) == ssm_parameter_2_value
    assert getattr(context, default_entry_name).get(string_list_default_name) == string_list_value.split(',')
    assert getattr(context, default_entry_name).get(secure_parameter_default_name) == secure_parameter_value

    time.sleep(10)
    context = multi_parameters(test_event,test_context)
    assert getattr(context, default_entry_name).get(ssm_parameter_default_name) == dummy_string
    assert getattr(context, default_entry_name).get(ssm_parameter_2_default_name) == dummy_string
    assert getattr(context, default_entry_name).get(string_list_default_name) == dummy_list.split(',')
    assert getattr(context, default_entry_name).get(secure_parameter_default_name) == dummy_string

    test_initialize()
    context = multi_parameters(test_event,test_context)
    assert getattr(context, default_entry_name).get(ssm_parameter_default_name) == dummy_string
    assert getattr(context, default_entry_name).get(ssm_parameter_2_default_name) == dummy_string
    assert getattr(context, default_entry_name).get(string_list_default_name) == dummy_list.split(',')
    assert getattr(context, default_entry_name).get(secure_parameter_default_name) == dummy_string
    
    time.sleep(10)
    context = multi_parameters(test_event,test_context)
    assert getattr(context, default_entry_name).get(ssm_parameter_default_name) == ssm_parameter_value
    assert getattr(context, default_entry_name).get(ssm_parameter_2_default_name) == ssm_parameter_2_value
    assert getattr(context, default_entry_name).get(string_list_default_name) == string_list_value.split(',')
    assert getattr(context, default_entry_name).get(secure_parameter_default_name) == secure_parameter_value
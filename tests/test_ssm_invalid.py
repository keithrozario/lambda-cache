from lambda_cache import ssm
from lambda_cache.exceptions import ArgumentTypeNotSupportedError, NoEntryNameError
from tests.context_object import LambdaContext

import pytest
from botocore.exceptions import ClientError
import toml

from tests.variables_data import *
from tests.helper_functions import update_parameter


# Test Non-existent parameter

@ssm.cache(parameter="/some/nonexist/parameter")
def parameter_not_exist_var_handler(event, context):
    return context

def test_non_existing_parameter():
    
    test_event = {'event_name': 'test'}
    test_context = LambdaContext()
    with pytest.raises(ClientError) as e:
        context = parameter_not_exist_var_handler(test_event, test_context)
        assert e['Error']['Code'] == "ParameterNotFound"

# Test invalid parameter
@ssm.cache(parameter=123, entry_name="hello")
def invalid_parameter(event, context):
    return context

def test_invalid_parameter():

    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        invalid_parameter({}, LambdaContext())
        assert e['Code'] == "ArgumentTypeNotSupportedError"

    with pytest.raises(NoEntryNameError) as e:
        ssm.get_entry(parameter=123, max_age_in_seconds=4)
        assert e['Code'] == "NoEntryNameError"
    
    with pytest.raises(NoEntryNameError) as e:
        ssm.get_entry(parameter={'dummy': 'dict'}, max_age_in_seconds=2)
        assert e['Code'] == "NoEntryNameError"
    
    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        ssm.get_entry(parameter=123, max_age_in_seconds=2, entry_name="hello")
        assert e['Code'] == "ArgumentTypeNotSupportedError"

    with pytest.raises(ArgumentTypeNotSupportedError) as e:
        ssm.get_entry(parameter=(123,123), max_age_in_seconds=2, entry_name="hello")
        assert e['Code'] == "ArgumentTypeNotSupportedError"
    
    with pytest.raises(NoEntryNameError) as e:
        ssm.get_entry(parameter=['abc','_'], max_age_in_seconds=2)
        assert e['Code'] == "NoEntryNameError"
    

# Test Non-existent parameter
@ssm.cache(parameter="/some/nonexist/parameter")
def parameter_not_exist_var_handler(event, context):
    return context

def test_non_existing_parameter():
    
    test_event = {'event_name': 'test'}
    test_context = LambdaContext()
    with pytest.raises(ClientError) as e:
        context = parameter_not_exist_var_handler(test_event, test_context)
        assert e['Error']['Code'] == "ParameterNotFound"
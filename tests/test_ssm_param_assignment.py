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

    ttl = 5

    param = ssm.get_entry(parameter=parameter, max_age_in_seconds=ttl)
    assert param == parameter_value_return
    
    update_parameter(parameter, dummy_value, parameter_type)
    param = ssm.get_entry(parameter=parameter, max_age_in_seconds=ttl)
    assert param == parameter_value_return

    time.sleep(ttl)
    param = ssm.get_entry(parameter=parameter, max_age_in_seconds=ttl)
    assert param == dummy_value_return
    param = ssm.get_entry(parameter=parameter, max_age_in_seconds=ttl)
    assert param == dummy_value_return

    time.sleep(ttl)
    update_parameter(parameter, parameter_value, parameter_type)
    param = ssm.get_entry(parameter=parameter, max_age_in_seconds=ttl)
    assert param == parameter_value_return
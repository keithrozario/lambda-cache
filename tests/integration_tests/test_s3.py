import time
import random
import string

from tests.variables_data import *
from tests.helper_functions import upload_object

from tests.integration_tests.helper_functions import get_message_from_lambda, get_serverless_config
from tests.helper_functions import get_s3_bucket_name

bucket_name = get_s3_bucket_name()
s3_key = "tests/s3/key.json"


def generic_test(function_name, ori_status, sleep_time=60):
    
    status = get_message_from_lambda(function_name) 
    assert status == ori_status

    upload_object('../test_env/test_data/s3_new.json', bucket_name, s3_key)
    status = get_message_from_lambda(function_name) 
    assert status == ori_status

    time.sleep(sleep_time)
    status = get_message_from_lambda(function_name) 
    assert status == "new"

    upload_object('../test_env/test_data/s3_old.json', bucket_name, s3_key)
    status = get_message_from_lambda(function_name) 
    assert status == "new"

    time.sleep(sleep_time)
    status = get_message_from_lambda(function_name) 
    assert status == ori_status


def test_initialize():

    upload_object('../test_env/test_data/s3_old.json', bucket_name, s3_key)


def test_s3_download():

    function_name = f"{service}-{stage}-s3_download"
    generic_test(function_name, "old", 5)

# Config Variables
config = get_serverless_config()
service = config['service']
stage = config['provider']['stage']

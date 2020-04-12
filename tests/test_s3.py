from lambda_cache import s3
import json
import time
import pytest

from tests.context_object import LambdaContext
from tests.helper_functions  import upload_object, get_s3_bucket_name, check_status_file

from lambda_cache import s3
from lambda_cache.exceptions import InvalidS3UriError

bucket_name = get_s3_bucket_name()
s3_key = "tests/s3/key.json"
s3Uri = f"s3://{bucket_name}/{s3_key}"


def test_initialize():

    upload_object('test_env/test_data/s3_old.json', bucket_name, s3_key)
    status = check_status_file(bucket_name, s3_key)
    assert status == "old"


def decorated_function_test(decorated_function, entry_name, ori_status, max_age_in_seconds):

    test_event = {'event_name': 'test'}
    test_context = LambdaContext()
    new_status = "new"

    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status
    
    # Update object and download
    upload_object('test_env/test_data/s3_new.json', bucket_name, s3_key)
    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status

    # Wait max_age_in_seconds call again
    time.sleep(max_age_in_seconds)
    return_status = decorated_function(test_event, test_context)
    assert return_status == new_status

    # Revert back to normal
    upload_object('test_env/test_data/s3_old.json', bucket_name, s3_key)
    return_status = decorated_function(test_event, test_context)
    assert return_status == new_status

    time.sleep(max_age_in_seconds)
    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status


# Test s3
@s3.cache(s3Uri=f"s3://{bucket_name}/{s3_key}", max_age_in_seconds=5, check_before_download=False)
def s3_download(event, context):
    with open(getattr(context, s3_key.split('/')[-1]), 'r') as file_data:
        status = json.loads(file_data.read())['status']

    return status

# Test Invalid Uri
@s3.cache(s3Uri=f"L3:--/{bucket_name}/{s3_key}", max_age_in_seconds=5, check_before_download=False)
def invalid_uri(event, context):
    status = True
    return status

# Test entry_name
@s3.cache(s3Uri=f"s3://{bucket_name}/{s3_key}", entry_name='temp_key.json', max_age_in_seconds=5, check_before_download=False)
def s3_download_entry_name(event, context):
    with open("/tmp/temp_key.json") as file_data:
        status = json.loads(file_data.read())['status']

    return status

# Test default seconds
@s3.cache(s3Uri=f"s3://{bucket_name}/{s3_key}", entry_name='temp_key.json', check_before_download=False)
def s3_default_age(event, context):
    with open("/tmp/temp_key.json") as file_data:
        status = json.loads(file_data.read())['status']

    return status

# Test non updated file
@s3.cache(s3Uri=f"s3://{bucket_name}/{s3_key}", max_age_in_seconds=5, entry_name='temp_key.json', check_before_download=True)
def s3_not_updated(event, context):
    with open("/tmp/temp_key.json") as file_data:
        status = json.loads(file_data.read())['status']

    return status


def test_decorated_functions():
    decorated_function_test(s3_download, False, max_age_in_seconds=5, ori_status="old")
    decorated_function_test(s3_download_entry_name, entry_name="temp_key.json", max_age_in_seconds=5, ori_status="old")
    decorated_function_test(s3_download, False, max_age_in_seconds=60, ori_status="old")
    not_refreshed_test(s3_not_updated, False, max_age_in_seconds=5, ori_status="old")
    

def test_invalid_s3Uri():
    with pytest.raises(InvalidS3UriError) as e:
        invalid_uri({}, LambdaContext)
        assert e == "InvalidS3UriError"


def test_get_entry():
    file_location = s3.get_entry(s3Uri=f"s3://{bucket_name}/{s3_key}", max_age_in_seconds=5, entry_name=False, check_before_download=True)
    with open(file_location, 'r') as file_data:
        status = json.loads(file_data.read())['status']
    assert status == "old"


def not_refreshed_test(decorated_function, entry_name, ori_status, max_age_in_seconds):
    """
    Special use-case where file is not updated to get 100% code coverage
    package will only check file's last_modified_date, and not download
    """

    test_event = {'event_name': 'test'}
    test_context = LambdaContext()

    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status
    
    # Update object and download
    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status

    # Wait max_age_in_seconds call again
    time.sleep(max_age_in_seconds)
    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status

    # Wait max_age_in_seconds call again
    time.sleep(max_age_in_seconds)
    return_status = decorated_function(test_event, test_context)
    assert return_status == ori_status
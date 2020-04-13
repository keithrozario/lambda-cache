# Reference

## SSM

### ssm.cache

Decorator function, meant to decorate invocation handler, but can be used to decorate any method within your lambda function.

```python
from lambda_cache import ssm

@ssm.cache(parameter='/production/app/var')
def handler(event, context):
    var = getattr(context,'var')
    response = do_something(var)
    return response
```

#### Parameters

* parameter(_str_): Name of Parameter is SSM Parameter Store
* max_age_in_seconds(_int_): Maximum acceptable age of a cache entry before a refresh must be executed (**_default: 60_**)
* entry_name(_str_): Name of entry in _context_ object. (**_default: paremeter.split('/')_**)

### ssm.get_entry

Get's the value of the ssm parameter from cache (forces a refresh from parameter store if the cache object is older than `max_age_in_seconds`)

```python
from lambda_cache import ssm

def handler(event, context):
    var = ssm.get_entry(parameter='/production/app/var',
                        max_age_in_seconds=300)
    response = do_something(var)
    return response
```

#### Parameters

* parameter(_str_): Name of Parameter is SSM Parameter Store
* max_age_in_seconds(_int_): Maximum acceptable age of a cache entry before a refresh must be executed (**_default: 60_**)
* entry_name(_str_): Name of entry in _context_ object. (**_default: paremeter.split('/')_**)

## Secrets Manager

### secrets_manager.cache

Decorator function, meant to decorate invocation handler, but can be used to decorate any method within your lambda function.

```python
@secrets_manager.cache(name='/prod/db/connection_string', max_age_in_seconds=10, entry_name='new_secret')
def call_with_entry_name(event, context):
    secret = getattr(context, 'new_secret')
    response do_something(secret)
    return response
```

#### Parameters

* name(_str_): Name of secret in secrets manager
* max_age_in_seconds(_int_): Maximum acceptable age of a cache entry before a refresh must be executed (**_default: 60_**)
* entry_name(_str_): Name of entry in _context_ object. (**_default: name.split('/')_**)

### secrets_manager.get_entry

Get's the value of the secret from cache (forces a refresh from secrets_manager if cache entry is older than `max_age_in_seconds`)

```python
@secrets_manager.cache(name='/prod/db/connection_string', max_age_in_seconds=300, entry_name='secret')
def call_with_entry_name(event, context):

    try:
        secret = getattr(context, 'secret')
        response = do_something(secret)
    except AuthenticationError:
        new_secret = secrets_manager.get_entry(name='/prod/db/connection_string',
                                               max_age_in_seconds=0,  # forces a reset of secret
                                               entry_name='secret')
        response = do_something(secret)
    
    return response
```

#### Parameters

* name(_str_): Name of secret in secrets manager
* max_age_in_seconds(_int_): Maximum acceptable age of a cache entry before a refresh must be executed (**_default: 60_**)
* entry_name(_str_): Name of entry in _context_ object. (**_default: name.split('/')_**)

## S3

Decorator function, meant to decorate invocation handler, but can be used to decorate any method within your lambda function.

### s3.cache

```python
from lambda_cache import s3

@s3.cache(s3Uri='s3://bucket_name/path/to/object.json', max_age_in_seconds=300)
def s3_download_entry_name(event, context):
    with open("/tmp/object.json") as file_data:
        status = json.loads(file_data.read())['status']

    return status
```
#### Parameters

* s3Uri(_str_): s3Uri of object to download in the form `s3://bucket-name/path/to/object`
* max_age_in_seconds(_int_): Maximum acceptable age of a cache entry before a refresh must be executed (**_default: 60_**)
* entry_name(_str_): Name of entry in _context_ object. (**_default: s3Uri.split('/')_**). _Note: this is the location of the downloaded file and not the content of the file itself_
* check_before_download(_bool_): Check object age before downloading (useful for large objects). Setting this to `True` will cause package to check if the object has been updated since the last cache refresh, and only download the object **if** the object has changed.

### s3.get_entry

Get's the value of the secret from cache (forces a refresh from secrets_manager if cache entry is older than `max_age_in_seconds`)

```python
def test_get_entry():
    file_location = s3.get_entry(s3Uri=f"s3://{bucket_name}/{s3_key}", max_age_in_seconds=5, entry_name=False, check_before_download=True)
    with open(file_location, 'r') as file_data:
        status = json.loads(file_data.read())['status']
```

#### Parameters

* s3Uri(_str_): s3Uri of object to download in the form `s3://bucket-name/path/to/object`
* max_age_in_seconds(_int_): Maximum acceptable age of a cache entry before a refresh must be executed (**_default: 60_**)
* entry_name(_str_): Name of entry in _context_ object. (**_default: s3Uri.split('/')_**). _Note: this is the location of the downloaded file and not the content of the file itself_
* check_before_download(_bool_): Check object age before downloading (useful for large objects). Setting this to `True` will cause package to check if the object has been updated since the last cache refresh, and only download the object **if** the object has changed.
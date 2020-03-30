# AWS Lambda Cache
Python utility for caching SSM parameters in AWS Lambda functions.

** THIS IS NOT WORKING YET, DO NOT USE **

## Simple use case

To cache a parameter for 300 seconds, simply decorate your handler function as follows:

```python

from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var', ttl_seconds=300)
def handler(event, context):

    cached_value = event.get('var')
    event_var = event.get('body')
    response = do_something(cached_value, event_var)

    return response

```

## Multiple variables

To cache multiple parameters, you can stack multiple decorators on top of each other:

```python

from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var_1', ttl_seconds=300)
@ssm_cache(parameter='/production/app/var_2', ttl_seconds=600)
def handler(event, context):

    cached_value_1 = event.get('var_1')
    cached_value_2 = event.get('var_2')
    event_var = event.get('body')
    response = do_something(cached_value, event_var)

    return response

```

## Rename parameter

The parameter is injected into the event of the handling function, using the last name of the parameter as the variable name in the event.

e.g. 
* /app1/prod/name -> event.name
* /app1/dev/config/startDate -> event.startDate (note case-sensitivity)

to give the parameter a specific variable name, use the var_name argument in the decorator call.

```python

from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/app1/prod/name', ttl_seconds=300, var_name='customer_name')
@ssm_cache(parameter='/app1/dev/config/startDate', ttl_seconds=600, var_name='customer_start_date')
def handler(event, context):

    cached_value_1 = event.get('customer_name')
    cached_value_2 = event.get('customer_start_date')
    response = do_something(cached_value_1, cached_value_2)

    return response

```

## Special configuration

To disable cache, and GetParameter on every invocation, set `ttl_seconds=0`,  to only get parameter once in the lifetime of the function, set `ttl_seconds` to some arbitary large number ~36000 (10 hours).

# Status

Currently supports parameters of type `String` and `SecureString`. `StringList` support is working but not tested.

# The End

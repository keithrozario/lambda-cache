# AWS Lambda Cache
Caching utility for AWS Lambda functions.

![PackageStatus](https://img.shields.io/static/v1?label=status&message=beta&color=red?style=flat-square) 
![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.6%20|%203.7|%203.8&color=blue?style=flat-square&logo=python)

![Test](https://github.com/keithrozario/aws_lambda_cache/workflows/Test/badge.svg) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/keithrozario/aws_lambda_cache.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/keithrozario/aws_lambda_cache/context:python)

# Basics

This is python package prioritizes simplicity over everything else. The goal is to provide the simplest way for developers to include caching in their AWS Lambda functions. 

Currently only SSM Parameters and Secrets from Secrets Manager are supported.

## Cache single parameter

To cache a parameter from ssm, decorate your handler function, and grab the parameter from the context object as follows:

```python
from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var')
def handler(event, context):
    var = context.get('var')
    response = do_something(var)
    return response
```

## Change cache settings

The default `ttl_seconds` settings is 60 seconds, it defines how long a parameter should be kept in cache before it is refreshed from ssm. To configure longer or shorter times, modify this argument in the decorator like so:

```python
from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var', ttl_seconds=300)
def handler(event, context):
    var = context.get('var')
    response = do_something(var)
    return response
```

## Change cache entry settings

For simplicity the name of the parameter is automatically shortened to the string after the last slash('/') character. This allows both `/production/app/var` and `test/app/var` resolve to just `var`. To over-ride this default, use the `entry_name` argument for the decorator:

```python
from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var', entry_name='new_var')
def handler(event, context):
    var = context.get('new_var')
    response = do_something(var)
    return response
```

## Cache multiple parameters

To cache multiple entries at once, pass a list of parameters to the parameter argument, and grab the parameters from `context['parameters']`.

```python
from aws_lambda_cache import ssm_cache

@ssm_cache(parameter=['/app/var1', '/app/var2'], entry_name='parameters')
def handler(event, context):
    var1 = context.get('parameters').get('var1')
    var2 = context.get('parameters').get('var2')
    response = do_something(var)
    return response
```

## Decorator stacking
If you wish to cache multiple parameters with different expiry times, stack the decorators. In this example, `var1` will be refreshed every 30 seconds, `var2` will be refreshed after 60.

Note: Decorator stacking performs one API call per decorator, while passing a list to the parameter argument results in just one API call for better performance.

```python
@ssm_cache(parameter='/production/app/var1', ttl_seconds=30)
@ssm_cache(parameter='/production/app/var2', ttl_seconds=60)
def handler(event, context):
    var1 = context.get('var1')
    var2 = context.get('var2')
    response = do_something(var)
    return response
```

## Cache invalidation

If you require a fresh value, you can force a refresh using the `get_ssm_cache` function, and setting the `ttl_seconds` argument to 0.

```python
from aws_lambda_cache import ssm_cache, get_ssm_cache

@ssm_cache(parameter='/production/app/var')
def handler(event, context):

    if event.get('refresh'):
        var = get_ssm_cache(parameter='/production/app/var', ttl_seconds=0)
    else:
        var = context.get('var')
    response = do_something(var)
    return response
```

To disable cache, and GetParameter on every invocation, set `ttl_seconds=0`,  to only get parameter once in the lifetime of the function, set `ttl_seconds` to some arbitary large number ~36000 (10 hours).

## Return Values

Caching supports `String`, `SecureString` and `StringList` parameters with no change required (ensure you have `kms:Decrypt` permission for `SecureString`). For simplicity, `StringList` parameters are automatically converted into list (delimited by '/').

# Secrets Manager

```python
from aws_lambda_cache import secret_cache

@secret_cache(name='/prod/db/conn_string')
def handler(event, context):
    conn_string = context.get('conn_string')
    return context
```

The secrets manager uses the same API as ssm, and hence supports all the previously mentioned features including `ttl_seconds`, `entry_name` and cache invalidation.

## Cache Invalidation

To invalidate a secret, use the `get_secret_cache`, setting the `ttl_seconds=0`.
```python
from aws_lambda_cache import secret_cache, get_secret_cache

@secret_cache(name='/prod/db/conn_string')
def handler(event, context):

    if event.get('refresh'):
        var = get_secret_cache(name='/prod/db/conn_string', ttl_seconds=0)
    else:
        var = context.get('conn_string')
    response = do_something(var)
    return response
```

## Return Values

Secrets Manager supports both string and binary secrets. For simplicity we will cache the secret in the format it is stored.
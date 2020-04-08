<h1 align="center"> lambda-cache </h1>
<h2 align="center"> Simple Caching for AWS Lambda</h2>

![PackageStatus](https://img.shields.io/static/v1?label=status&message=beta&color=blueviolet?style=flat-square) ![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.6%20|%203.7|%203.8&color=blue?style=flat-square&logo=python)

![Build](https://github.com/keithrozario/lambda_cache/workflows/Build/badge.svg?branch=release) [![Coverage Status](https://coveralls.io/repos/github/keithrozario/lambda-cache/badge.svg?branch=release)](https://coveralls.io/github/keithrozario/lambda-cache?branch=release) [![Documentation Status](https://readthedocs.org/projects/simple-lambda-cache/badge/?version=latest)](https://simple-lambda-cache.readthedocs.io/en/latest/?badge=latest)

[![PyPI version](https://badge.fury.io/py/lambda-cache.svg)](https://badge.fury.io/py/lambda-cache) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 

# Basics

_lambda_cache_ prioritizes simplicity over performance and flexibility. The goal is to provide the **simplest** way for developers to cache api calls in their Lambda functions.

Currently only SSM Parameters and Secrets from Secrets Manager are supported. S3 and generic function support is coming soon.

## Cache single parameter

To cache a parameter from ssm, decorate your handler function:

```python
from lambda_cache import ssm

@ssm.cache(parameter='/production/app/var')
def handler(event, context):
    var = context.get('var')
    response = do_something(var)
    return response
```
All invocations of this function over in the next minute will reference the parameter from the function's internal cache, without making a network call to ssm. After one minute has lapsed, the the next invocation will invoke `get_parameter` to refresh the cache.

## Change cache settings

The default `ttl_seconds` settings is 60 seconds (1 minute), it defines how long a parameter should be kept in cache before it is refreshed from ssm. To configure longer or shorter times, modify this argument in the decorator:

```python
from lambda_cache import ssm

@ssm.cache(parameter='/production/app/var', ttl_seconds=300)
def handler(event, context):
    var = context.get('var')
    response = do_something(var)
    return response
```

_Note: The caching logic runs only at invocation of the function. A 15 minute lambda function will not refresh the parameter, unless explicitly refreshed using `get_entry`.The package is primary interested in caching 'across' invocations rather than 'within' one invocation_

## Change cache entry settings

The name of the parameter is shortened to the string after the last slash('/') character of its name. This means `/production/app/var` and `test/app/var` resolve to just `var`. To over-ride this default, use `entry_name`:

```python
from lambda_cache import ssm

@ssm.cache(parameter='/production/app/var', entry_name='new_var')
def handler(event, context):
    var = context.get('new_var')
    response = do_something(var)
    return response
```

## Cache multiple parameters

To cache multiple entries at once, pass a list of parameters to the parameter argument, and grab the parameters from `context['parameters']`.

```python
from lambda_cache import ssm

@ssm.cache(parameter=['/app/var1', '/app/var2'], entry_name='parameters')
def handler(event, context):
    var1 = context.get('parameters').get('var1')
    var2 = context.get('parameters').get('var2')
    response = do_something(var)
    return response
```

_Note: we use the `get_parameters` API call for boto3, which makes a single network call for multiple parameters. You can group all parameters types in a single call, with `String` and `SecureString` parameters returned as strings, while `StringList` parameters are returned a python lists._

## Decorator stacking
If you wish to cache multiple parameters with different expiry times, stack the decorators. In this example, `var1` will be refreshed every 30 seconds, `var2` will be refreshed after 60.

```python
@ssm.cache(parameter='/production/app/var1', ttl_seconds=30)
@ssm.cache(parameter='/production/app/var2', ttl_seconds=60)
def handler(event, context):
    var1 = context.get('var1')
    var2 = context.get('var2')
    response = do_something(var)
    return response
```
_Note: Decorator stacking performs one API call per decorator, which might result is slower performance._

## Cache invalidation

If you require a fresh value at some point of the code, you can force a refresh using the `get_entry` function, and setting the `ttl_seconds` argument to 0.

```python
from lambda_cache import ssm

@ssm.cache(parameter='/prod/var')
def handler(event, context):

    if event.get('refresh'):
        # refresh parameter
        var = ssm.get_entry(parameter='/prod/var', ttl_seconds=0)
    else:
        var = context.get('var')
    
    response = do_something(var)
    return response
```

## Return Values

Caching supports `String`, `SecureString` and `StringList` parameters with no change required (ensure you have `kms:Decrypt` permission for `SecureString`). For simplicity, the package takes away the heavy lifting of dealing with these different parameter types. `StringList` parameters are automatically converted into list (delimited by '/'), while `String` and `SecureString` both return the single string value of the parameter.

# Secrets Manager

Secret support is similar, but uses the `secrets_manager` decorator.

```python
from lambda_cache import secrets_manager

@secrets_manager.cache(name='/prod/db/conn_string')
def handler(event, context):
    conn_string = context.get('conn_string')
    return context
```

Secrets Managers supports all the previously mentioned features including `ttl_seconds`, `entry_name` and cache invalidation.

## Cache Invalidation

To invalidate a secret, use the `get_entry` method, setting `ttl_seconds=0`.
```python
from lambda_cache import secrets_manager

@secrets_manager.cache(name='/prod/db/conn_string')
def handler(event, context):

    if event.get('refresh'):
        var = secrets_manager.get_entry(name='/prod/db/conn_string', ttl_seconds=0)
    else:
        var = context.get('conn_string')
    response = do_something(var)
    return response
```

## Return Values

Secrets Manager supports both string and binary secrets. For simplicity we will cache the secret in the format it is stored. It is up to the calling application to process the return as Binary or Strings.

# Credit

Project inspired by:
* [SSM-Cache](https://github.com/alexcasalboni/ssm-cache-python)
* [middy](https://github.com/middyjs/middy)

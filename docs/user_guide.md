# User Guide

_simple_lambda_cache_ prioritizes simplicity over performance and flexibility. The goal of the package is to provide the **simplest** way for developers to cache api calls in their Lambda functions.

Currently only SSM Parameters and Secrets from Secrets Manager are supported.

## SSM - Parameter Store

### Cache single parameter

To cache a parameter from ssm, decorate your handler function:

```python
from simple_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var')
def handler(event, context):
    var = context.get('var')
    response = do_something(var)
    return response
```
All invocations of this function over in the next minute will reference the parameter from the function's internal cache, rather than making a network call to ssm. After one minute, the the next invocation will invoke `get_parameter` to refresh the cache.

### Change cache expiry

The default `ttl_seconds` settings is 60 seconds (1 minute), it defines how long a parameter should be kept in cache before it is refreshed from ssm. To configure longer or shorter times, modify this argument like so:

```python
from simple_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var', ttl_seconds=300)
def handler(event, context):
    var = context.get('var')
    response = do_something(var)
    return response
```

_Note: The caching logic runs only at invocation, regardless of how long the function runs. A 15 minute lambda function will not refresh the parameter, unless explicitly refreshed using get_cache_ssm. The library is primary interested in caching 'across' invocation rather than 'within' an invocation_

### Change cache entry settings

The name of the parameter is simply shortened to the string after the last slash('/') character of its name. This means `/production/app/var` and `test/app/var` resolve to just `var`. To over-ride this default, use `entry_name`:

```python
from simple_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var', entry_name='new_var')
def handler(event, context):
    var = context.get('new_var')
    response = do_something(var)
    return response
```

### Cache multiple parameters

To cache multiple entries at once, pass a list of parameters to the parameter argument, and grab the parameters from `context['parameters']`.

```python
from simple_lambda_cache import ssm_cache

@ssm_cache(parameter=['/app/var1', '/app/var2'], entry_name='parameters')
def handler(event, context):
    var1 = context.get('parameters').get('var1')
    var2 = context.get('parameters').get('var2')
    response = do_something(var)
    return response
```

Under the hood, we us the `get_parameters` API call for boto3, which translate to a single network call for multiple parameters. You can group all parameters types in a single call, including `String`, `StringList` and `SecureString`. `StringList` will return as a list, while all other types will return as plain-text strings.

### Decorator stacking
If you wish to cache multiple parameters with different expiry times, stack the decorators. In this example, `var1` will be refreshed every 30 seconds, `var2` will be refreshed after 60.

```python
@ssm_cache(parameter='/production/app/var1', ttl_seconds=30)
@ssm_cache(parameter='/production/app/var2', ttl_seconds=60)
def handler(event, context):
    var1 = context.get('var1')
    var2 = context.get('var2')
    response = do_something(var)
    return response
```
_Note: Decorator stacking performs one API call per decorator, which might result is slower performance_

### Cache invalidation

If you require a fresh value at some point of the code, you can force a refresh using the `get_ssm_cache` function, and setting the `ttl_seconds` argument to 0.

```python
from simple_lambda_cache import ssm_cache, get_ssm_cache

@ssm_cache(parameter='/prod/var')
def handler(event, context):

    if event.get('refresh'):
        # refresh parameter
        var = get_ssm_cache(parameter='/prod/var', ttl_seconds=0)
    else:
        var = context.get('var')
    
    response = do_something(var)
    return response
```

To disable cache, set `ttl_seconds=0`.

To only get parameter once in the lifetime of the function, set `ttl_seconds` to some arbitary large number ~36000 (10 hours).

### Return Values

Caching supports `String`, `SecureString` and `StringList` parameters with no change required (ensure you have `kms:Decrypt` permission for `SecureString`). For simplicity, `StringList` parameters are automatically converted into list (delimited by '/'), while `String` and `SecureString` both return the single string value of the parameter.

## Secrets Manager

### Cache single secret

Secret support is similar, but uses the `secret_cache` decorator.

```python
from simple_lambda_cache import secret_cache

@secret_cache(name='/prod/db/conn_string')
def handler(event, context):
    conn_string = context.get('conn_string')
    return context
```

Secrets Managers supports all the previously mentioned features including `ttl_seconds`, `entry_name` and cache invalidation.

### Change Cache expiry

The default `ttl_seconds` settings is 60 seconds (1 minute), it defines how long a parameter should be kept in cache before it is refreshed from ssm. To configure longer or shorter times, modify this argument like so:

```python
from simple_lambda_cache import secret_cache

@secret_cache(name='/prod/db/conn_string', ttl_seconds=300)
def handler(event, context):
    var = context.get('conn_string')
    response = do_something(var)
    return response
```

_Note: The caching logic runs only at invocation, regardless of how long the function runs. A 15 minute lambda function will not refresh the parameter, unless explicitly refreshed using get_cache_ssm. The library is primary interested in caching 'across' invocation rather than 'within' an invocation_

### Change Cache entry settings

The name of the secret is simply shortened to the string after the last slash('/') character of the secret's name. This means `/prod/db/conn_string` and `/test/db/conn_string` resolve to just `conn_string`. To over-ride this default, use `entry_name`:

```python
from simple_lambda_cache import secret_cache

@secret_cache(name='/prod/db/conn_string', entry_name='new_var')
def handler(event, context):
    var = context.get('new_var')
    response = do_something(var)
    return response
```

### Decorator stacking

If you wish to cache multiple secrets, you can use decorator stacking.

```python
@secret_cache(name='/prod/db/conn_string', ttl_seconds=30)
@secret_cache(name='/prod/app/elk_username_password', ttl_seconds=60)
def handler(event, context):
    var1 = context.get('conn_string')
    var2 = context.get('elk_username_password')
    response = do_something(var)
    return response
```

Note: Decorator stacking performs one API call per decorator, which might result is slower performance.

### Cache Invalidation

To invalidate a secret, use the `get_secret_cache`, setting the `ttl_seconds=0`.
```python
from simple_lambda_cache import secret_cache, get_secret_cache

@secret_cache(name='/prod/db/conn_string')
def handler(event, context):

    if event.get('refresh'):
        var = get_secret_cache(name='/prod/db/conn_string', ttl_seconds=0)
    else:
        var = context.get('conn_string')
    response = do_something(var)
    return response
```

### Return Values

Secrets Manager supports both string and binary secrets. For simplicity we will cache the secret in the format it is stored. It is up to the calling application to process the return as Binary or Strings.
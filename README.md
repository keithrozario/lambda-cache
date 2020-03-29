# AWS Lambda Cache
Python utility for caching SSM parameters in AWS Lambda functions.

# Proposed solution

## Simple use case

To cache a parameter for 5 minutes, simply decorate your handle function as follows:

```python

from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var', ttl_seconds=300)
def handler(event, context):

    cached_value = event.get('_production_app_var')
    event_var = event.get('body')
    response = do_something(cached_value, event_var)

    return response

```

## Multiple variables

To cache multiple parameters, you can stack multiple decorators on top of each other:

```python

from aws_lambda_cache import ssm_cache

@ssm_cache(parameter='/production/app/var_1', ttl=300)
@ssm_cache(parameter='/production/app/var_2', ttl=600)
def handler(event, context):

    # all '/' characters are replaced with '_' characters
    cached_value_1 = event.get('_production_app_var_1')
    cached_value_2 = event.get('_production_app_var_2')
    event_var = event.get('body')
    response = do_something(cached_value, event_var)

    return response

```

## Rename parameter

The variable is injected into the event parameter of the handling function. To provide a specific variable name, use the `var_name` parameter. This allows you to map multiple possible parameters into a single event variable (e.g. for prod, dev, test) using environment variables. In the example below `var_1` and `var_2` are set by the build pipeline corresponding to the different environments we're building. 

```python

from aws_lambda_cache import ssm_cache

@ssm_cache(parameter=os.environ['var_1'], ttl=300, var_name='var_1')
@ssm_cache(parameter=os.environ['var_2'], ttl=600, var_name='var_2)
def handler(event, context):

    cached_value_1 = event.get('var_1')
    cached_value_2 = event.get('var_2')
    event_var = event.get('body')
    response = do_something(cached_value, event_var)

    return response

```

# Status

Currently work in progress

# The End

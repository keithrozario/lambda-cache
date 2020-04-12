ssm_parameter = "/lambda_cache/something"
ssm_parameter_value = "Dummy Value 1"
ssm_parameter_default_name = "something"
ssm_parameter_replaced_var_name = "variable_1"

ssm_parameter_2 = "/lambda_cache/test/something_else"
ssm_parameter_2_value = "Dummy Value 2"
ssm_parameter_2_default_name = "something_else"

secure_parameter = "/lambda_cache/test/secure/somethingsecure"
secure_parameter_value = "This is secure"
secure_parameter_default_name = "somethingsecure"

long_name_parameter = "/lambda_cache/test/this/is/a/long/parameter/value/zzzzzzz/9/10/11"
long_name_value = "Long name"
long_name_default_name = "11"

string_list_parameter = "/lambda/cache/test/somelist"
string_list_value = "a,b,c"
string_list_default_name = "somelist"

# Secret variables
secret_name_string = "/lambda_cache/test/secret_string"
secret_name_string_value = "This is a secret /@#$"
secret_string_default_name = "secret_string"

secret_name_binary = "/lambda_cache/test/secret_binary"
secret_name_binary_value = "this is a secret in binary".encode('utf-8')
secret_binary_default_name = "secret_binary"

default_entry_name = "context_lambda_cache"

# S3 variables
s3_key = "tests/s3/key.json"
s3_bucket_ssm_param = "/lambda-cache/s3/bucket_name"
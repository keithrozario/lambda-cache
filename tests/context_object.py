
class LambdaContext(object):
    """ Dummy Lambda Context Object"""

    def __init__(self, invokeid="1234", context_objs=None, client_context=None, invoked_function_arn=None):
        dummy_value = "_"

        self.aws_request_id = invokeid
        self.log_group_name = dummy_value
        self.log_stream_name = dummy_value
        self.function_name = dummy_value
        self.memory_limit_in_mb = dummy_value
        self.function_version = dummy_value
        self.invoked_function_arn = invoked_function_arn

        # self.client_context = make_obj_from_dict(ClientContext, client_context)
        # if self.client_context is not None:
        #     self.client_context.client = make_obj_from_dict(Client, self.client_context.client)
        # self.identity = make_obj_from_dict(CognitoIdentity, context_objs)

    def get_remaining_time_in_millis(self):
        return "No time left"

    def log(self, msg):
        print ("logging out")
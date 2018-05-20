from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class JSONSuccess(Response):
    def __init__(self, result, *args, **kwargs):
        response = {"data": result}
        super().__init__(response, *args, **kwargs)


class JSONError(Response):
    def __init__(self, message, *args, **kwargs):
        response = {"error": message}
        super().__init__(response, *args, **kwargs)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# Error codes
LOG_IN_FAILED = 'LOGIN_FAILED'
ACCESS_DENIED = 'ACCESS_DENIED'
INSTANCE_DOES_NOT_EXIST = "INSTANCE_DOES_NOT_EXIST"

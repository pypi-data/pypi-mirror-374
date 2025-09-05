# exceptions.py


class CustomException(Exception):

    def __init__(self, exce_msg):
        super().__init__(exce_msg)
        self.message = exce_msg


class AuthorizationException(CustomException):
    pass


class RequestException(CustomException):
    pass


class ErrorException(CustomException):
    pass


class EntityException(CustomException):
    pass

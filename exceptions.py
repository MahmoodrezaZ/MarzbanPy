class BadResponse(BaseException):
    pass


class BearerRequired(BaseException):
    pass


class ExistanceError(BaseException):
    pass

class PermissionDenied(BaseException):
    pass

class ValidationError(BaseException):
    pass

class NotExistsError(BaseException):
    pass

class SuperFastAPIError(Exception):
    """Base class for SuperFastAPI errors."""


class ApiVersionError(SuperFastAPIError):
    pass


class FunctionNotFoundError(SuperFastAPIError):
    pass


class ImmutableViolationError(SuperFastAPIError):
    pass


class TestFailureError(SuperFastAPIError):
    pass


class AuthError(SuperFastAPIError):
    def __init__(self, message: str, status_code: int = 403):
        super().__init__(message)
        self.status_code = status_code


class ResolutionError(SuperFastAPIError):
    pass


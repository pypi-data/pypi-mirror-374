# Copyright Hewlett Packard Enterprise Development LP


class NotImplementedException(Exception):
    """Exception raised for methods that are not implemented."""

    def __init__(self, message="This method is not implemented."):
        super().__init__(message)


class HTTPUnauthorizedException(Exception):
    """Exception raised for HTTP 401 Unauthorized errors."""

    def __init__(
        self,
        message="HTTP 401 Unauthorized: Access is denied due to invalid credentials.",
    ):
        super().__init__(message)


class SimilaritySearchFailureException(Exception):
    """Exception raised when a similarity search operation fails."""

    def __init__(self, message="Similarity search operation failed."):
        super().__init__(message)


class UnexpectedStatus(Exception):
    """Raised by api functions when the response status an unexpected status"""

    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        self.content = content

        super().__init__(
            f"Unexpected status code: {status_code}\n\nResponse content:\n{content.decode(errors='ignore')}"
        )


class UnexpectedResponse(Exception):
    """Exception raised when an API response is not as expected."""

    def __init__(self, status_code: int, response: bytes):
        self.status_code = status_code
        self.response = response

        super().__init__(
            f"Unexpected response: {status_code}\n\nResponse content:\n{response.decode(errors='ignore')}"
        )

# Copyright Hewlett Packard Enterprise Development LP

from typing import Any, Dict, Optional

import httpx
from attrs import define, evolve, field


@define
class AuthenticatedSession:
    """
    Class for handling REST API requests.
    This class is responsible for making HTTP requests to a specified URL and
    handling the response.
    """

    _headers: Dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: Optional[httpx.Timeout] = field(
        default=300, kw_only=True, alias="timeout"
    )
    _client: Optional[httpx.Client] = field(default=None, init=False)
    _httpx_args: Dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")

    uri: str = field(kw_only=True, alias="uri")
    username: str = field(kw_only=True, alias="username")
    password: str = field(kw_only=True, alias="password")
    # sha256_pinned_cert:str
    # token is already prefixed with "Bearer " as per the DI API
    token: str = field(kw_only=True, alias="token")
    auth_header_name: str = field(
        default="Authorization",
        kw_only=True,
        alias="auth_header_name",
    )

    def with_headers(self, headers: Dict[str, str]) -> "AuthenticatedSession":
        """Get a new session matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_timeout(self, timeout: httpx.Timeout) -> "AuthenticatedSession":
        """Get a new session matching this one with a new timeout (in seconds)"""
        if self._client is not None:
            self._client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_httpx_client(self, client: httpx.Client) -> "AuthenticatedSession":
        """Manually set the underlying httpx.Client

        **NOTE**: This will override any other settings on the client, including headers, and timeout.
        """
        self._client = client
        return self

    def get_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set"""
        if self._client is None:
            self._headers[self.auth_header_name] = self.token
            self._client = httpx.Client(
                base_url=self.uri,
                headers=self._headers,
                timeout=self._timeout,
                verify=False,
                **self._httpx_args,
            )
        return self._client

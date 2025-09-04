# Copyright Hewlett Packard Enterprise Development LP

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.sessions.session import Session
from pydi_client.errors import NotImplementedException
from pydi_client.logger import get_logger  # Importing the logger utility

from typing import Any, Dict
import httpx

# Initialize logger for this module
logger = get_logger()


class AuthAPI:

    @classmethod
    def login(cls, *, uri, username, password) -> AuthenticatedSession:
        """
        Login to the DI server using the provided username and password
        It returns the AuthenticatedSession object
        """
        logger.info("Attempting to log in with username: %s", username)

        s = Session(uri=uri)  # type: ignore

        _kwargs: Dict[str, Any] = {"method": "post", "url": "/api/v1/login"}
        _kwargs["data"] = {"username": username, "password": password}

        response = s.get_httpx_client().request(
            **_kwargs,
        )
        logger.debug("Login response status code: %s", response.status_code)

        if response.status_code != httpx.codes.OK:
            logger.error("Login failed with status code: %s", response.status_code)
            raise httpx.HTTPStatusError(
                f"Login failed with status code {response.status_code}",
                request=response.request,
                response=response,
            )

        # create authenticated session using token from response
        token = response.json().get("Authorization")
        if not token:
            logger.error("Login failed, no JWT token in response")
            raise httpx.HTTPStatusError(
                "Login failed, no JWT token in response",
                request=response.request,
                response=response,
            )

        # create authenticated session
        authenticated_session = AuthenticatedSession(  # type: ignore
            uri=uri,  # type: ignore
            token=token,  # type: ignore
            username=username,  # type: ignore
            password=password,  # type: ignore
        )
        logger.info("Login successful for username: %s", username)
        return authenticated_session

    @classmethod
    def refresh(cls, *, session: AuthenticatedSession):
        """
        Refresh the session
        This method uses the AuthenticatedSession class to refresh the session
        """
        logger.info("Refreshing session for username: %s", session.username)

        new_session = AuthAPI.login(
            uri=session.uri,
            username=session.username,
            password=session.password,
        )

        session.token = new_session.token
        session.username = new_session.username
        session.password = new_session.password
        session.set_httpx_client(new_session.get_httpx_client())
        logger.info("Session refreshed successfully for username: %s", session.username)

    @classmethod
    def logout(cls, *, session: AuthenticatedSession):
        """
        Logout from the server
        This method uses the AuthenticatedSession class to logout from the server
        It returns the session object
        """
        logger.info("Attempting to log out for username: %s", session.username)
        raise NotImplementedException(message="Logout not implemented")

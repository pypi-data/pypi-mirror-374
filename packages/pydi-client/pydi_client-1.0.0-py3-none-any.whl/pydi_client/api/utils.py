# Copyright Hewlett Packard Enterprise Development LP

import httpx
import json
from httpx import Response
from typing import Any, Dict, Callable

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.api.auth import AuthAPI
from pydi_client.errors import (
    HTTPUnauthorizedException,
    UnexpectedResponse,
    UnexpectedStatus,
)
from pydi_client.data.collection_manager import ListCollection, ListPipelines

from pydi_client.logger import get_logger  # Importing the logger utility

# Initialize logger for this module
logger = get_logger()


def execute_with_retry(
    session, request_func: Callable, **kwargs: Dict[str, Any]
) -> Response:
    """
    Executes an HTTP request with retry logic for unauthorized errors.

    Args:
        session: The session object (AuthenticatedSession or Session).
        request_func: The function to execute the HTTP request.
        kwargs: Arguments to pass to the request function.

    Returns:

    Raises:
        HTTPUnauthorizedException: If the request fails even after retrying.
    """
    resp = request_func(**kwargs)
    if resp is not None:
        logger.debug(
            "Response Status Code: %s, Response Text: %s",
            resp.status_code,
            resp.text,
        )

        if resp.status_code == 401 or resp.status_code == 403:
            logger.warning(
                "Unauthorized access detected. Attempting to refresh session."
            )

            if isinstance(session, AuthenticatedSession):
                logger.info("Refreshing session for authenticated user.")
                AuthAPI.refresh(session=session)  # Refresh the session
                request_func = (
                    session.get_httpx_client().request
                )  # refresh the function
                return request_func(**kwargs)
            else:
                raise HTTPUnauthorizedException(
                    "Unauthorized access. Session is not authenticated."
                )

    return resp


def build_response(*, response: httpx.Response, response_cls: Any) -> Any:
    if httpx.codes.OK <= response.status_code <= httpx.codes.CREATED:

        response_200 = None

        if not response.content or response.content.strip() == b"":
            return response_200

        try:
            _response_200 = response.json()
            if response_cls in (ListCollection, ListPipelines):
                response_200 = response_cls(root=_response_200)
            else:
                response_200 = response_cls(**_response_200)
        except TypeError as e:
            raise UnexpectedResponse(response.status_code, response.content) from e
        except json.JSONDecodeError as e:
            raise UnexpectedResponse(response.status_code, response.content) from e
        return response_200

    if response.status_code == 401:
        raise HTTPUnauthorizedException(
            "Unauthorized access. Please check your credentials or refresh session"
        )
    else:
        raise UnexpectedStatus(response.status_code, response.content)

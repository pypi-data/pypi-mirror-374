# Copyright Hewlett Packard Enterprise Development LP

from typing import Any, Dict, Union, Type

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.sessions.session import Session

from pydi_client.data.schema import (
    V1SchemasResponse,
    V1ListSchemasResponse,
)

from pydi_client.api.utils import execute_with_retry, build_response
from pydi_client.logger import get_logger  # Importing the logger utility

# Initialize logger for this module
logger = get_logger()


class MethodFactory:
    BASE_URL = "/api/v1/schemas"

    def get_schema(self, name):
        return self._build("get", f"{self.BASE_URL}/{name}")

    def get_schemas(self):
        return self._build("get", f"{self.BASE_URL}")

    def _build(self, method, endpoint):
        return {"method": method, "url": endpoint}


class DataModelFactory:

    @staticmethod
    def get_schema() -> Type[V1SchemasResponse]:
        return V1SchemasResponse

    @staticmethod
    def get_schemas() -> Type[V1ListSchemasResponse]:
        return V1ListSchemasResponse


class SchemaAPI:
    """
    A client API for interacting with schema objects.
    This class provides methods to retrieve information about schemas
    from a backend service. It uses a session object to handle authenticated
    requests and supports retry mechanisms for robust communication.
    """

    def __init__(self, session: Union[Session, AuthenticatedSession]):
        self._session = session
        logger.info("SchemaAPI initialized with session: %s", type(session).__name__)

    def get_schema(self, *, name: str) -> V1SchemasResponse:
        logger.info("Retrieving schema with name: %s", name)
        kwargs: Dict[str, Any] = MethodFactory().get_schema(name)
        logger.debug("Request parameters for get_schema: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Received response for get_schema: %s", response.text)
        return build_response(
            response=response, response_cls=DataModelFactory.get_schema()
        )

    def get_schemas(self) -> V1ListSchemasResponse:
        logger.info("Retrieving all schemas")
        kwargs: Dict[str, Any] = MethodFactory().get_schemas()
        logger.debug("Request parameters for get_models: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Received response for get_models: %s", response.text)
        return build_response(
            response=response, response_cls=DataModelFactory.get_schemas()
        )

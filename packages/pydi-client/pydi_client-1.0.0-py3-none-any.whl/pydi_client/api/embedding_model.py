# Copyright Hewlett Packard Enterprise Development LP

from typing import Any, Dict, Union, Type

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.sessions.session import Session


from pydi_client.data.model import (
    V1ModelsResponse,
    V1ListModelsResponse,
)

from pydi_client.api.utils import execute_with_retry, build_response
from pydi_client.logger import get_logger  # Importing the logger utility

# Initialize logger for this module
logger = get_logger()


class MethodFactory:
    BASE_URL = "/api/v1/models"

    def get_model(self, name):
        return self._build("get", f"{self.BASE_URL}/{name}")

    def get_models(self):
        return self._build("get", f"{self.BASE_URL}")

    def _build(self, method, endpoint):
        return {"method": method, "url": endpoint}


class DataModelFactory:

    @staticmethod
    def get_model() -> Type[V1ModelsResponse]:
        return V1ModelsResponse

    @staticmethod
    def get_models() -> Type[V1ListModelsResponse]:
        return V1ListModelsResponse


class EmbeddingModelAPI:
    """
    A client API for interacting with embedding models.
    This class provides methods to retrieve information about embedding models
    from a backend service. It uses a session object to handle authenticated
    requests and supports retry mechanisms for robust communication.
    """

    def __init__(self, session: Union[Session, AuthenticatedSession]):
        self._session = session
        logger.info(
            "EmbeddingModelAPI initialized with session: %s", type(session).__name__
        )

    def get_model(self, *, name: str) -> V1ModelsResponse:
        logger.info("Retrieving model with name: %s", name)

        kwargs: Dict[str, Any] = MethodFactory().get_model(name)
        logger.debug("Request parameters for get_model: %s", kwargs)

        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Received response for get_model with name: %s", name)

        return build_response(
            response=response, response_cls=DataModelFactory.get_model()
        )

    def get_models(self) -> V1ListModelsResponse:
        logger.info("Retrieving all models")

        kwargs: Dict[str, Any] = MethodFactory().get_models()
        logger.debug("Request parameters for get_models: %s", kwargs)

        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Received response for get_models: %s", response.text)

        return build_response(
            response=response, response_cls=DataModelFactory.get_models()
        )

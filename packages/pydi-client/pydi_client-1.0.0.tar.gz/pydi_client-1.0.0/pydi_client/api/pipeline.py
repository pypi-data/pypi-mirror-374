# Copyright Hewlett Packard Enterprise Development LP

from typing import Any, Dict, Union, List, Type, Optional

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.sessions.session import Session
from pydi_client.data.pipeline import (
    V1CreatePipeline,
    V1CreatePipelineResponse,
    V1DeletePipelineResponse,
    FilterItem,
)
from pydi_client.data.collection_manager import (
    V1PipelineResponse,
    ListPipelines,
)
from pydi_client.api.utils import execute_with_retry, build_response
from pydi_client.logger import get_logger  # Importing the logger utility

# Initialize logger for this module
logger = get_logger()


class MethodFactory:
    BASE_URL = "/api/v1/pipelines"

    def create_pipeline(self):
        return self._build("post", f"{self.BASE_URL}")

    def get_pipeline(self, name):
        return self._build("get", f"{self.BASE_URL}/{name}")

    def get_pipelines(self):
        return self._build("get", f"{self.BASE_URL}")

    def delete_pipeline(self, name):
        return self._build("delete", f"{self.BASE_URL}/{name}")

    def _build(self, method, endpoint):
        return {"method": method, "url": endpoint}


class DataModelFactory:

    @staticmethod
    def get_pipeline() -> Type[V1PipelineResponse]:
        return V1PipelineResponse

    @staticmethod
    def get_pipelines() -> Type[ListPipelines]:
        return ListPipelines

    @staticmethod
    def create_pipeline() -> Type[V1CreatePipelineResponse]:
        return V1CreatePipelineResponse

    @staticmethod
    def delete_pipeline() -> Type[V1DeletePipelineResponse]:
        return V1DeletePipelineResponse


class PipelineAPI:
    """
    PipelineAPI - a class to manage pipelines
    This class provides methods to create, update, and delete pipelines.
    It uses the Session or AuthenticatedSession class to make HTTP requests to the server.
    """

    def __init__(self, session: Union[AuthenticatedSession, Session]):
        self._session = session
        logger.info("PipelineAPI initialized with session: %s", type(session).__name__)

    def create_pipeline(
        self,
        *,
        name: str,
        pipeline_type: str,
        event_filter_object_suffix: List[str],
        event_filter_max_object_size: int,
        schema: Optional[str] = None,
        model: Optional[str] = None,
        custom_func: Optional[str] = None,
    ) -> V1CreatePipelineResponse:
        """
        Create a new pipeline.

        Args:
            pipeline_name (str): The name of the pipeline.
            pipeline_type (str): The type of the pipeline.
            pipeline (str): The pipeline definition.
            buckets (Optional[Union[str, list]]): Buckets to assign to the pipeline.

        Returns:
            Optional[Union[Any, Pipeline]]: The created pipeline or None if the request failed.
        """
        logger.info("Creating pipeline with name: %s, type: %s", name, pipeline_type)

        filter_item = FilterItem(
            objectSuffix=event_filter_object_suffix,
            maxObjectSize=event_filter_max_object_size,
        )
        body = V1CreatePipeline(
            name=name,
            type=pipeline_type,
            model=model,
            eventFilter=filter_item,
            schema=schema,
            customFunction=custom_func,
        )

        kwargs: Dict[str, Any] = MethodFactory().create_pipeline()
        kwargs["json"] = body.model_dump(exclude_none=True)

        logger.debug("Request payload for create_pipeline: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Pipeline created successfully: %s", name)
        return build_response(
            response=response, response_cls=DataModelFactory.create_pipeline()
        )

    def get_pipeline(self, *, name: str) -> V1PipelineResponse:
        """
        Get a pipeline by name.

        Args:
            pipeline_name (str): The name of the pipeline.

        Returns:
            Optional[Union[Any, Pipeline]]: The requested pipeline or None if the request failed.
        """
        logger.info("Fetching pipeline with name: %s", name)

        kwargs: Dict[str, Any] = MethodFactory().get_pipeline(name=name)

        logger.debug("Request payload for get_pipeline: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Fetched pipeline successfully: %s", name)
        return build_response(
            response=response, response_cls=DataModelFactory.get_pipeline()
        )

    def get_pipelines(self) -> ListPipelines:
        """
        Get all pipelines.

        Returns:
            Optional[Union[Any, List[Pipeline]]]: A list of pipelines or None if the request failed.
        """
        logger.info("Fetching all pipelines")

        kwargs: Dict[str, Any] = MethodFactory().get_pipelines()

        logger.debug("Request payload for get_pipelines: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Fetched all pipelines successfully")
        return build_response(
            response=response, response_cls=DataModelFactory.get_pipelines()
        )

    def delete_pipeline(self, *, name: str) -> V1DeletePipelineResponse:
        """
        Delete a pipeline by name.

        Args:
            pipeline_name (str): The name of the pipeline to delete.

        Returns:
            Optional[Union[Any, Pipeline]]: The deleted pipeline or None if the request failed.
        """
        logger.info("Deleting pipeline with name: %s", name)

        kwargs: Dict[str, Any] = MethodFactory().delete_pipeline(name=name)

        logger.debug("Request payload for delete_pipeline: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Deleted pipeline successfully: %s", name)
        return build_response(
            response=response, response_cls=DataModelFactory.delete_pipeline()
        )

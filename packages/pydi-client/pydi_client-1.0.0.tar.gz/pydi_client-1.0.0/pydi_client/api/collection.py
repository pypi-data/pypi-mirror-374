# Copyright Hewlett Packard Enterprise Development LP

from typing import Any, Dict, Optional, Union, List, Type

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.sessions.session import Session
from pydi_client.data.collection_manager import (
    V1CollectionResponse,
    V1CreateCollection,
    V1DeleteCollectionResponse,
    ListCollection,
)
from pydi_client.data.pipeline import BucketUpdateResponse
from pydi_client.errors import (
    NotImplementedException,
)
from pydi_client.api.utils import execute_with_retry, build_response
from pydi_client.logger import get_logger  # Importing the logger utility

# Initialize logger for this module
logger = get_logger()


class MethodFactory:
    BASE_URL = "/api/v1/collections"

    def create_collection(self):
        return self._build("post", f"{self.BASE_URL}")

    def get_collection(self, name):
        return self._build("get", f"{self.BASE_URL}/{name}")

    def get_collections(self):
        return self._build("get", f"{self.BASE_URL}")

    def delete_collection(self, name):
        return self._build("delete", f"{self.BASE_URL}/{name}")

    def assign_buckets(self, name):
        return self._build("post", f"{self.BASE_URL}/{name}/assignBuckets")

    def unassign_buckets(self, name):
        return self._build("post", f"{self.BASE_URL}/{name}/unassignBuckets")

    def _build(self, method, endpoint):
        return {"method": method, "url": endpoint}


class DataModelFactory:

    @staticmethod
    def get_collection() -> Type[V1CollectionResponse]:
        return V1CollectionResponse

    @staticmethod
    def get_collections() -> Type[ListCollection]:
        return ListCollection

    @staticmethod
    def create_collection() -> Type[V1CollectionResponse]:
        return V1CollectionResponse

    @staticmethod
    def assign_buckets() -> Type[BucketUpdateResponse]:
        return BucketUpdateResponse

    @staticmethod
    def unassign_buckets() -> Type[BucketUpdateResponse]:
        return BucketUpdateResponse

    @staticmethod
    def delete_collection() -> Type[V1DeleteCollectionResponse]:
        return V1DeleteCollectionResponse


class CollectionAPI:
    """
    CollectionAPI - a class to manage collections
    This class provides methods to create, update, and delete collections, assign/unassign buckets to collection
    It uses the Session or AuthenticatedSession class to make HTTP requests to the server.
    """

    def __init__(self, session: Union[AuthenticatedSession, Session]):
        self._session = session
        logger.info(
            "CollectionAPI initialized with session: %s", type(session).__name__
        )

    def create_collection(
        self,
        *,
        name: str,
        pipeline: str,
        buckets: Optional[Union[Any, List[str]]] = [],
    ) -> V1CollectionResponse:
        logger.info("Creating collection with name: %s, pipeline: %s", name, pipeline)
        body = V1CreateCollection(
            name=name,
            pipeline=pipeline,
            buckets=buckets,
        )

        kwargs: Dict[str, Any] = MethodFactory().create_collection()
        kwargs["json"] = body.model_dump()

        logger.debug("Request payload for create_collection: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Collection created successfully: %s", name)
        return build_response(
            response=response, response_cls=DataModelFactory.create_collection()
        )

    def get_collections(
        self,
    ) -> ListCollection:
        logger.info("Fetching all collections")
        kwargs: Dict[str, Any] = MethodFactory().get_collections()

        logger.debug("Request payload for get_collections: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Fetched all collections successfully")
        return build_response(
            response=response, response_cls=DataModelFactory.get_collections()
        )

    def get_collection(self, *, name: str) -> V1CollectionResponse:
        logger.info("Fetching collection with name: %s", name)
        kwargs: Dict[str, Any] = MethodFactory().get_collection(name=name)

        logger.debug("Request payload for get_collection: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Fetched collection successfully: %s", name)
        return build_response(
            response=response, response_cls=DataModelFactory.get_collection()
        )

    def delete_collection(self, *, name: str) -> V1DeleteCollectionResponse:
        logger.info("Deleting collection with name: %s", name)
        kwargs: Dict[str, Any] = MethodFactory().delete_collection(name=name)

        logger.debug("Request payload for delete_collection: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Deleted collection successfully: %s", name)
        return build_response(
            response=response, response_cls=DataModelFactory.delete_collection()
        )

    def assign_buckets_to_collection(
        self, *, collection_name: str, buckets: List[str]
    ) -> BucketUpdateResponse:
        logger.info("Assigning buckets to collection: %s", collection_name)
        kwargs: Dict[str, Any] = MethodFactory().assign_buckets(name=collection_name)
        kwargs["json"] = {"buckets": buckets}

        logger.debug("Request payload for assign_buckets_to_collection: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info("Buckets assigned successfully to collection: %s", collection_name)
        return build_response(
            response=response, response_cls=DataModelFactory.assign_buckets()
        )

    def unassign_buckets_from_collection(
        self, *, collection_name: str, buckets: List[str]
    ) -> BucketUpdateResponse:
        logger.info("Unassigning buckets from collection: %s", collection_name)
        kwargs: Dict[str, Any] = MethodFactory().unassign_buckets(name=collection_name)
        kwargs["json"] = {"buckets": buckets}

        logger.debug("Request payload for unassign_buckets_from_collection: %s", kwargs)
        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )
        logger.info(
            "Buckets unassigned successfully from collection: %s", collection_name
        )
        return build_response(
            response=response, response_cls=DataModelFactory.unassign_buckets()
        )

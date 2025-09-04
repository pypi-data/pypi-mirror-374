# Copyright Hewlett Packard Enterprise Development LP

from pydi_client.sessions.session import Session
from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.api.collection import CollectionAPI
from pydi_client.api.pipeline import PipelineAPI
from pydi_client.api.embedding_model import EmbeddingModelAPI
from pydi_client.api.schema import SchemaAPI
from pydi_client.api.search import SimilaritySearchAPI
from pydi_client.api.auth import AuthAPI
from pydi_client.errors import NotImplementedException

from pydi_client.data.collection_manager import (
    ListCollection,
    ListPipelines,
    V1PipelineResponse,
    V1CollectionResponse,
    V1DeleteCollectionResponse,
)
from pydi_client.data.pipeline import (
    BucketUpdateResponse,
    V1CreatePipelineResponse,
    V1DeletePipelineResponse,
)

from pydi_client.data.model import (
    V1ModelsResponse,
    V1ListModelsResponse,
)

from pydi_client.data.schema import (
    V1SchemasResponse,
    V1ListSchemasResponse,
)

from typing import Union, Any, List, Dict, Optional


class DIClient:
    """
    DIClient
    The `DIClient` class serves as a client interface for interacting with the Data Intelligence (DI) solution.
    It provides methods to retrieve and interact with various data entities such as collections, pipelines, schemas,
    and embedding models. Additionally, it supports performing similarity searches within collections.
    This class is designed for general-purpose usage and is intended for scenarios where non-administrative
    operations are required. For administrative operations, such as managing users, permissions, or system-level
    configurations, the `DIAdminClient` class should be used instead.

    Purpose:
    --------
    The `DIClient` class simplifies the interaction with the DI solution by abstracting the underlying API calls
    and providing a Pythonic interface for common operations. It is particularly useful for developers and data
    scientists who need to work with DI collections, pipelines, schemas, and embedding models in their workflows.

    Key Features:
    -------------
    1. Retrieve specific or all collections, pipelines.
    2. Perform similarity searches within a specified collection.
    3. Provides a session object for managing API interactions.

    Usage:
    ------
    - Use this class for non-administrative tasks such as querying collections, retrieving pipelines, or performing
        similarity searches.
    - Avoid using this class for administrative tasks. For such operations, use the `DIAdminClient` class.
    """

    def __init__(self, *, uri=None) -> None:
        self._session = Session(uri=uri)  # type: ignore

    @property
    def session(self) -> Session:
        """
        Property to get the session object.

        Returns:
            Session: The session object used for making API requests. This session is initialized with the provided URI.

        """
        return self._session

    def get_collection(self, *, name: str) -> V1CollectionResponse:
        """
        Retrieve a collection by its name.

        Args:
            name (str): The name of the collection to retrieve. This is a required keyword-only argument.

        Returns:
            V1CollectionResponse: The collection object corresponding to the
            specified name.

        Example usage:
            ```python
                client = DIClient(uri="https://example.com")
                collection = client.get_collection(name="example_collection")
                print(collection)
                # Output: V1CollectionResponse(
            #     name="example_collection",
            #     buckets=["bucket-1", "bucket-2"],
            #     pipeline="rag-pipeline"
            # )
            ```
        """
        return CollectionAPI(self.session).get_collection(name=name)

    def get_all_collections(self) -> ListCollection:
        """
        Retrieves all collections available in the system.

        Returns:
            V1ListCollectionsResponse: A response object containing a list of
            collections available in the system.

        Example usage:
            ```python
                client = DIClient(uri="https://example.com")
                collections = client.get_all_collections()
                for collection in collections:
                    print(collection.name)
            # Output:
            ListCollection(
                root=[
                    ListCollectionItem(id="1", name="collection1"),
                    ListCollectionItem(id="2", name="collection2")
                ]
            )
            ```
        """

        return CollectionAPI(self.session).get_collections()

    def get_pipeline(self, *, name: str) -> V1PipelineResponse:
        """
        Retrieve a pipeline by its name.
        This method fetches a pipeline object from the PipelineAPI using the provided name.

        Args:
            name (str): The name of the pipeline to retrieve. This is a required keyword-only argument.

        Returns:
            DescribePipelineRecordResponse: The response object containing details about the pipeline.

        Example usage:
                ```python
                client = DIClient(uri="https://example.com")
                pipeline = client.get_pipeline(name="example_pipeline")
                print(pipeline)
                # Output: V1PipelineResponse(
                #     name="example_pipeline",
                #     type="rag",
                #     model="example_model",
                #     customFunction="custom_processing_function",
                #     eventFilter={"objectSuffix": ["*.txt", "*.pdf"],
                #                  "maxObjectSize": 10485760},
                #     schema="example_schema"
                # )
                ```
        """
        return PipelineAPI(self.session).get_pipeline(name=name)

    def get_all_pipelines(self) -> ListPipelines:
        """
        Retrieves all pipelines available in the system.

        Returns:
            ListPipelineRecordsResponse: A response object containing a list of
            pipelines available in the system.

        Example usage:
            ```python
                client = DIClient(uri="https://example.com")
                pipelines = client.get_all_pipelines()
                for pipeline in pipelines.pipelines:
                    print(pipeline.name)
            # Output:
            ListPipelines(
                root=[
                    ListPipeline(id="1", name="pipeline1"),
                    ListPipeline(id="2", name="pipeline2")
                ]
            )
            ```
        """
        return PipelineAPI(self.session).get_pipelines()

    def similarity_search(
        self,
        *,
        access_key: str,
        secret_key: str,
        collection_name: str,
        query: str,
        top_k: int,
        search_parameters: Union[Any, Dict[str, Any]] = None,
    ) -> Union[Any, List[Dict[str, Any]]]:
        """
        Perform a similarity search on a specified collection using the provided query.
        This method interacts with the SimilaritySearchAPI to retrieve the most relevant
        results from a collection based on the given query. The results are ranked by
        similarity, and the top `k` results are returned.

        Args:
            query (str): The search query string used to find similar items in the collection.
            collection_name (str): The name of the collection to search within.
            top_k (int): The number of top similar results to retrieve.
            access_key (str): The access key for authentication with the API.
            secret_key (str): The secret key for authentication with the API.
            search_parameters (Optional[Union[Any, Dict[str, Any]]]): Additional search parameters
                that can be passed to the API for fine-tuning the search behavior.

        Returns:
            Union[Any, List[Dict[str, Any]]]: A list of dictionaries containing the top `k` similar results, or another data type depending on the API's response.

        Example usage:
            ```python
            client = DIClient(session)
            results = client.similarity_search(
                query="machine learning",
                collection_name="research_papers",
                top_k=5,
                access_key="your_access_key",
                secret_key="your_secret_key",
                search_parameters={"metric": "cosine", "ef_search": "100"}
            )
            print(results)
            [
                {
                    "dataChunk": "chunk1",
                    "score": 0.9,
                    "chunkMetadata": {
                        "objectKey": "value",
                        "startCharIndex": 1,
                        "endCharIndex": 2,
                        "bucketName": "string",
                        "pageLabel": "string",
                        "versionId": "string",
                    }
                }
            ]
            ```
        """
        return SimilaritySearchAPI(self.session).search(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
            access_key=access_key,
            secret_key=secret_key,
            search_parameters=search_parameters,
        )


class DIAdminClient(DIClient):
    """
    DIAdminClient
    The `DIAdminClient` class is an extension of the `DIClient` class, designed specifically for administrative operations
    within the Data Intelligence (DI) platform. This class provides methods to manage collections, pipelines, schemas,
    and their associated resources. It is intended for use cases where administrative privileges are required to perform
    operations such as creating, deleting, or modifying collections, pipelines, and schemas.

    Purpose:
    ---------
    The `DIAdminClient` is tailored for scenarios where administrative-level API interactions are necessary.
    It provides a higher level of control over the DI platform's resources, enabling administrators to configure
    and manage the system effectively.

    When to Use:
    ------------
    - Use this class when you need to perform administrative tasks such as:

        - Creating or deleting collections.

        - Assigning or unassigning buckets to/from collections.

        - Creating or deleting pipelines.

        - Creating or deleting schemas.

    - This class is specifically designed for admin APIs. For non-admin APIs, use the `DIClient` class instead.

    Initialization:
    ---------------
    The `DIAdminClient` requires authentication credentials (username and password) to establish an authenticated session
    with the DI platform. Upon initialization, it creates an authenticated session that is used for all subsequent API calls.
    --------
    """

    def __init__(self, *, uri: str, username: str, password: str) -> None:
        super().__init__(uri=uri)

        # create session with auth
        self._authenticated_session = AuthAPI.login(
            uri=uri, username=username, password=password
        )

    @property
    def authenticated_session(self) -> AuthenticatedSession:
        """
        Property to get the authenticated session object.

        Returns: 
        AuthenticatedSession: The authenticated session object used for making API requests.This session is initialized with the provided URI, username, password, and token.

        """
        return self._authenticated_session

    def create_collection(
        self, *, name: str, pipeline: str, buckets: Optional[List[str]] = None
    ) -> V1CollectionResponse:
        """
        Creates a new collection using the specified pipeline.
        If buckets are provided, they will be associated with the collection and inline embedding generation will be triggered.
        If buckets are not provided, the collection will be created but embedding generation will be deferred until buckets are assigned to the collection.

        Args:
            name (str): The name of the collection to be created. This should be unique.
            pipeline (str): The name of the pipeline to be associated with the collection.
            buckets (Optional[List[str]], optional): A list of bucket names. Defaults to None.

        Returns:
            V1CollectionResponse: The created collection object.

        Example usage:
            ```python
            # Example usage of create_collection
            client = DIAdminClient(uri="https://example.com", username="admin", password="password")
            collection = client.create_collection(
                name="example_collection",
                pipeline="data_ingestion_pipeline",
                buckets=["bucket1", "bucket2"]
            )
            print(collection)
            # Sample Output:
            # V1CollectionResponse(
            #     name="example_collection",
            #     pipeline="data_ingestion_pipeline",
            #     buckets=["bucket1", "bucket2"]
            # )
            ```
        """
        if buckets is None:
            buckets = []

        return CollectionAPI(session=self.authenticated_session).create_collection(
            name=name,
            buckets=buckets,
            pipeline=pipeline,
        )

    def delete_collection(self, *, name: str) -> V1DeleteCollectionResponse:
        """
        Deletes a collection by its name.

        Args:
            name (str): The name of the collection to be deleted.

        Returns:
            None: This method does not return any value.

        Example Usage:
        ```python
            client = DIAdminClient(uri="https://example.com", username="admin", password="password")
            resp = client.delete_collection(name="example_collection")
            print(resp)
            # Output:
            # V1DeleteCollectionResponse(
            #     success=True,
            #     message="Collection 'example_collection' has been deleted."
            # )
        ```
        """
        return CollectionAPI(session=self.authenticated_session).delete_collection(
            name=name
        )

    def assign_buckets_to_collection(
        self, *, collection_name: str, buckets: List[str]
    ) -> BucketUpdateResponse:
        """
        Assigns a list of buckets to a specified collection.
        This enables inline embedding generation for the specified buckets.

        Args:
            collection_name (str): The name of the collection to which the buckets
                will be assigned.
            buckets (List[str]): A list of bucket names to be assigned to the
                specified collection.

        Returns:
            BucketUpdateResponse: The response object containing details about the
            updated collection and assigned buckets.

        Example Usage:
            ```python
            # Initialize the DIAdminClient
            client = DIAdminClient(uri="http://example.com", username="admin", password="password")
            # Define the collection name and buckets
            collection_name = "my_collection"
            buckets = ["bucket1", "bucket2", "bucket3"]
            # Assign buckets to the collection
            response = client.assign_buckets_to_collection(
                collection_name=collection_name,
                buckets=buckets
            )
            print(response)
            # Output:
            # BucketUpdateResponse(
            #     sucess=true,
            #     message="Buckets assigned successfully to collection 'my_collection'."
            # )
            ```
        Notes:
            - This method is typically used for enabling the user buckets for intelligence using an existing collection.
        """

        return CollectionAPI(
            session=self.authenticated_session
        ).assign_buckets_to_collection(collection_name=collection_name, buckets=buckets)

    def unassign_buckets_from_collection(
        self, *, collection_name: str, buckets: List[str]
    ) -> BucketUpdateResponse:
        """
        Unassigns one or more buckets from a specified collection.

        Args:
            collection_name (str): The name of the collection from which the buckets will be unassigned.
            buckets (List[str]): A list of bucket names to be unassigned.

        Returns:
            BucketUpdateResponse: The response object containing details about the updated collection
            after the buckets have been unassigned.

        Example usage:
            ```python
            # Example usage of unassign_buckets_from_collection
            client = DIAdminClient(uri="http://example.com", username="admin", password="password")

            # Unassign multiple buckets
            response = client.unassign_buckets_from_collection(
                collection_name="example_collection",
                buckets=["bucket_1", "bucket_2", "bucket_3"]
            )
            print(response)
            # Output:
            # BucketUpdateResponse(
            #     success=true,
            #     message="Buckets unassigned successfully from collection 'example_collection'."
            # )
            ```
        """
        return CollectionAPI(
            session=self.authenticated_session
        ).unassign_buckets_from_collection(
            collection_name=collection_name, buckets=buckets
        )

    def create_pipeline(
        self,
        *,
        name: str,
        pipeline_type: str,
        event_filter_object_suffix: List[str],
        event_filter_max_object_size: Optional[int] = None,
        schema: Optional[str] = None,
        model: Optional[str] = None,
        custom_func: Optional[str] = None,
    ) -> V1CreatePipelineResponse:
        """
        Creates a new pipeline with the specified configuration.

        Args:
            name (str): The name of the pipeline to be created.
            pipeline_type (str): The type of the pipeline (e.g., "rag", "metadata").
            model Optional (str): The model associated with the pipeline.
            custom_func Optional (str): The custom function to be used in the pipeline.
            event_filter_object_suffix (List[str]): A list of file suffixes to filter events. Ex - ["*.txt", "*.pdf"]
            event_filter_max_object_size (int): The maximum object size for event filtering. Ex - 10485760
            schema Optional (str): The schema definition for the pipeline.

        Returns:
            V1CreatePipelineResponse: The response object containing details of the created pipeline.

        Example usage:
            ```python
            client = DIAdminClient(
                uri="http://example.com",
                username="admin",
                password="password"
            )
            pipeline_data = client.create_pipeline(
                name="example_pipeline",
                pipeline_type="rag",
                model="example_model",
                custom_func="custom_processing_function",
                event_filter_object_suffix=["*.txt", "*.pdf"],
                event_filter_max_object_size=10485760,
                schema="example_schema"
            )
            print(pipeline_data)
            # Output: V1CreatePipelineResponse(
            #     success=true,
            #     message="Pipeline 'example_pipeline' created successfully."
            # )
            ```
        """

        return PipelineAPI(session=self.authenticated_session).create_pipeline(
            name=name,
            pipeline_type=pipeline_type,
            model=model,
            custom_func=custom_func,
            event_filter_object_suffix=event_filter_object_suffix,
            event_filter_max_object_size=event_filter_max_object_size,
            schema=schema,
        )

    def delete_pipeline(self, *, name: str) -> V1DeletePipelineResponse:
        """
        Deletes a pipeline with the specified name.

        Args:
            name (str): The name of the pipeline to be deleted.

        Returns:
            V1DeletePipelineResponse: The response object containing details about the deleted pipeline.

        Example usage:
            ```python
            # Initialize the DIAdminClient
            client = DIAdminClient(uri="http://example.com", username="admin", password="password")

            # Delete a pipeline by name
            response = client.delete_pipeline(name="example_pipeline")
            print(response)
            # Output:
            # V1DeletePipelineResponse(
            #     message="Pipeline successfully deleted"
            #     success=True,
            # )
            ```
        """
        return PipelineAPI(session=self.authenticated_session).delete_pipeline(
            name=name
        )

    def get_schema(self, *, name: str) -> V1SchemasResponse:
        """
        Retrieve a schema by its name.
        This method fetches a schema object from the SchemaAPI using the provided name.

        Args:
            name (str): The name of the schema to retrieve. This is a required keyword-only argument.

        Returns:
            V1SchemaResponse: The response object containing details about the schema.

        Example usage:
            ```python
                client = DIAdminClient(uri="https://example.com", username="admin", password="password")
                schema = client.get_schema(name="example_schema")
                print(schema)
                # Output: V1SchemaResponse(
                #     name="example_schema",
                #     type="...",
                #     schema=[SchemaItem]
                # )
        """
        return SchemaAPI(session=self.authenticated_session).get_schema(name=name)

    def get_all_schemas(self) -> V1ListSchemasResponse:
        """
        Retrieves all schemas available in the system.

        Returns:
            V1ListSchemasResponse: A response object containing a list of
            schemas available in the system.

        Example usage:
            ```python
                client = DIAdminClient(uri="https://example.com", username="admin", password="password")
                schemas = client.get_all_schemas()
                print(schemas)
                # Output: V1ListSchemasResponse(
                #     schemas=[SchemaRecordSummary]
                # )
            ```
        """
        return SchemaAPI(session=self.authenticated_session).get_schemas()

    def get_embedding_model(self, *, name: str) -> V1ModelsResponse:
        """
        Retrieve an embedding model by its name.
        This method fetches an embedding model object from the EmbeddingModelAPI using the provided name.

        Args:
            name (str): The name of the embedding model to retrieve. This is a required keyword-only argument.

        Returns:
            V1ModelsResponse: The response object containing details about the embedding model.

        Example usage:
            ```python
                client = DIAdminClient(uri="https://example.com", username="admin", password="password")
                model = client.get_embedding_model(name="example_model")
                print(model)
                # Output: V1ModelsResponse(
                #     name="example_model",
                #     modelName="...",
                #     capabilities="...",
                #     dimension=...,  # e.g., 768
                #     maximumTokens=...,  # e.g., 512
                #     version="..."
                # )
            ```
        """
        return EmbeddingModelAPI(self.authenticated_session).get_model(name=name)

    def get_all_embedding_models(self) -> V1ListModelsResponse:
        """
        Retrieves all embedding models available in the system.

        Returns:
            V1ListModelsResponse: A response object containing a list of
            embedding models available in the system.

        Example usage:
            ```python
                client = DIAdminClient(uri="https://example.com", username="admin", password="password")
                models = client.get_all_embedding_models()
                print(models[0])
                # Output: V1ModelsResponse(
                #     models=[ModelRecordSummary],
                # )
            ```
        """
        return EmbeddingModelAPI(self.authenticated_session).get_models()

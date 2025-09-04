# Copyright Hewlett Packard Enterprise Development LP

from http import HTTPStatus
from typing import Any, Dict, Union, List

from pydi_client.sessions.authenticated_session import AuthenticatedSession
from pydi_client.sessions.session import Session
from pydi_client.errors import SimilaritySearchFailureException
from pydi_client.api.utils import execute_with_retry, build_response
from pydi_client.data.pipeline import V1SimilaritySearchResponse
from pydi_client.logger import get_logger  # Importing the logger utility

# Initialize logger for this module
logger = get_logger()


class SimilaritySearchAPI:
    """
    Class to perform similarity search using the PyDI API.
    """

    def __init__(self, session: Union[AuthenticatedSession, Session]):
        self._session = session
        logger.info(
            "SimilaritySearchAPI initialized with session: %s", type(session).__name__
        )

    def search(
        self,
        *,
        access_key: str,
        secret_key: str,
        collection_name: str,
        query: str,
        top_k: int,
        search_parameters: Union[Dict[str, Any]] = None,
    ) -> V1SimilaritySearchResponse:
        """
        Perform a similarity search in the specified collection.

        Args:
            collection_name (str): The name of the collection to search in.
            query (str): The query string to search for.
            top_k (int): The number of top results to return.
            access_key (str): The access key for S3 credentials.
            secret_key (str): The secret key for S3 credentials.
            search_parameters (Dict[str, Any]): Additional search parameters.

        Returns:
            V1SimilaritySearchResponse: The search results.

            Sample response: List of similar data chunks
                {
                "success": True,
                "message": "Similarity search completed successfully.",
                "results": [
                    {
                        "score": 0,
                        "dataChunk": "string",
                        "chunkMetadata": {
                            "objectKey": "string",
                            "startCharIndex" : 1,
                            "endCharIndex" : 2,
                            "bucketName": "string",
                            "pageLabel": "string",
                            "versionId": "string",
                        }
                    }
                ]
                }
        """
        logger.info(
            "Performing similarity search in collection: %s with query: %s and top_k: %d",
            collection_name,
            query,
            top_k,
        )

        kwargs: Dict[str, Any] = {"method": "POST", "url": "/api/v1/similaritySearch"}

        body = {
            "collectionName": collection_name,
            "query": query,
            "topK": top_k,
            "credentials": {"accessKey": access_key, "secretKey": secret_key},
            "searchParams": search_parameters,
        }

        kwargs["json"] = body

        logger.debug("Request payload for similarity search: %s", kwargs)

        response = execute_with_retry(
            session=self._session,
            request_func=self._session.get_httpx_client().request,
            **kwargs,
        )

        logger.debug("Similarity search response status code: %s", response.status_code)

        if response.status_code == HTTPStatus.OK:
            logger.info(
                "Similarity search completed successfully for collection: %s",
                collection_name,
            )
            # validate response
            resp = build_response(
                response=response, response_cls=V1SimilaritySearchResponse
            )
            return resp.model_dump().get("results", [])

        else:
            logger.error(
                "Similarity search failed for collection: %s with status code: %s and response: %s",
                collection_name,
                response.status_code,
                response.text,
            )
            raise SimilaritySearchFailureException(
                f"Similarity search failed with status code {response.status_code}: {response.text}"
            )

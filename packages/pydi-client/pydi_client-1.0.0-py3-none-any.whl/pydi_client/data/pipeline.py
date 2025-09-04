# Copyright Hewlett Packard Enterprise Development LP

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class V1DeletePipelineResponse(BaseModel):

    """
    Response model for deleting a pipeline.
    This model contains fields to indicate the status of the delete operation,
    any errors that occurred, and a message providing additional information.

    Attributes:
        status (Optional[str]): Status of the delete operation.
        Status (Optional[str]): Alternative case for status of the delete operation.
        Error (Optional[Dict[Any, Any]]): Error message if the delete operation fails.
        success (Optional[bool]): Indicates if the delete operation was successful.
        message (Optional[str]): Message providing additional information about the operation.
    """
    status: Optional[str] = Field(
        default_factory=str, description="Status of the delete operation"
    )
    Status: Optional[str] = Field(
        default_factory=str,
        description="Status of the delete operation (alternative case)",
    )
    Error: Optional[Dict[Any, Any]] = Field(
        default_factory=dict, description="Error message if the delete operation fails"
    )
    success: Optional[bool] = Field(
        default=None, description="Indicates if the delete operation was successful"
    )
    message: Optional[str] = Field(
        default=None, description="Message providing additional information about the operation"
    )


class FilterItem(BaseModel):
    """
    Represents a filter item used in event filtering for pipelines.
    Attributes:
        objectSuffix (List[str]): List of suffixes for objects to filter.
        maxObjectSize (int): Maximum size of the object to filter.
    """
    objectSuffix: List[str]
    maxObjectSize: Optional[int] = Field(default=None)


class V1CreatePipeline(BaseModel):
    """
    Represents a request to create a pipeline.
    Attributes:
        name (str): Name of the pipeline.
        type (str): Type of the pipeline.
        model (Optional[str]): Optional model associated with the pipeline.
        eventFilter (FilterItem): Event filter criteria for the pipeline.
        schema (Optional[str]): Optional schema for the pipeline.
        customFunction (Optional[str]): Optional custom function for the pipeline.
    """
    name: str
    type: str
    model: Optional[str]
    eventFilter: FilterItem
    schema: Optional[str]
    customFunction: Optional[str]


class V1CreatePipelineResponse(BaseModel):
    """
    Response model for creating a pipeline.
    This model contains fields to indicate the success of the creation operation
    and a message providing additional information.

    Attributes:
        success (bool): Indicates if the pipeline creation was successful.
        message (str): Message providing additional information about the operation.
    """
    success: bool
    message: str


class BucketUpdateResponse(BaseModel):
    """
    Response model for updating buckets in a collection.
    This model contains fields to indicate the success of the update operation
    and a message providing additional information.
    Attributes:
        success (bool): Indicates if the bucket update was successful.
        message (str): Message providing additional information about the operation.
    """
    success: bool
    message: str


class NodeWithScore(BaseModel):
    """
    Represents a node with its associated score and metadata.
    Attributes:
        score (float): Score associated with the node.
        dataChunk (str): Data chunk associated with the node.
        chunkMetadata (Optional[Dict[str, Any]]): Optional metadata associated with the data chunk
    """
    score: float
    dataChunk: str
    chunkMetadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class V1SimilaritySearchResponse(BaseModel):
    """
    Response model for similarity search in a collection.
    This model contains fields to indicate the success of the search operation,
    a message providing additional information, and the results of the search.
    Attributes:
        success (bool): Indicates if the similarity search was successful.
        message (str): Message providing additional information about the operation.
        results (Optional[List[NodeWithScore]]): List of nodes with their scores returned by the search.
    """
    success: bool
    message: str
    results: Optional[List[NodeWithScore]] = Field(default_factory=list)

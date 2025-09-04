# Copyright Hewlett Packard Enterprise Development LP

from pydantic import BaseModel, Field
from typing import List


class V1ModelsResponse(BaseModel):
    """
    Response model for listing available models.
    This model contains fields to represent the system model name, model name,
    capabilities, dimensionality, maximum tokens supported by the model, and the version of the model.
    Attributes:
        name (str): System model name.
        modelName (str): Model name.
        capabilities (List[str]): List of capabilities such as embedding, large language model, etc.
        dimension (int): Model dimensionality.
        maximumTokens (int): Maximum token size supported by the model.
        version (str): Model version.
    """

    name: str = Field(..., description="system model name")
    modelName: str = Field(..., description="model name")
    capabilities: List[str] = Field(...,
                                    description="embedding, large language model etc")
    dimension: int = Field(..., description="model dimensionality")
    maximumTokens: int = Field(...,
                               description="max token size supported by the model")
    version: str = Field(..., description="model version")


class ModelRecordSummary(BaseModel):
    """
    Represents a summary of a model record.
    Attributes:
        id (str): Unique identifier for the model record.
        name (str): Name of the model record.
    """
    id: str
    name: str


class V1ListModelsResponse(BaseModel):
    """
    Response model for listing available models.
    This model contains a list of model records.
    Attributes:
        models (List[ModelRecordSummary]): List of model records.
    """
    models: List[ModelRecordSummary]

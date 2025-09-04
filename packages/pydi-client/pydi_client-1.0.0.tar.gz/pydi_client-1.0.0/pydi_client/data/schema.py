# Copyright Hewlett Packard Enterprise Development LP

from pydantic import BaseModel, Field
from typing import List


class SchemaItem(BaseModel):
    """
    Represents a schema item with a name and type.
    Attributes:
        name (str): Name of the schema field.
        type (str): Type of the schema field.
    """
    name: str = Field(..., description="field name")
    type: str = Field(..., description="field type")


class V1SchemasResponse(BaseModel):
    """
    Represents a response containing schema information.
    This model contains fields to represent the schema name, type, and a list of schema items.
    Attributes:
        name (str): Name of the schema.
        type (str): Type of the schema.
        schema (List[SchemaItem]): List of schema fields.
    """
    name: str = Field(..., description="schema name")
    type: str = Field(..., description="schema type")
    schema: List[SchemaItem] = Field(
        ..., alias="schema", description="list of schema fields"
    )


class SchemaRecordSummary(BaseModel):
    """
    Represents a summary of a schema record.
    Attributes:
        id (str): Unique identifier for the schema record.
        name (str): Name of the schema record.
    """
    id: str
    name: str


class V1ListSchemasResponse(BaseModel):
    """
    Response model for listing available schemas.
    This model contains a list of schema records.
    Attributes:
        schemas (List[SchemaRecordSummary]): List of schema records.
    """
    schemas: List[SchemaRecordSummary]

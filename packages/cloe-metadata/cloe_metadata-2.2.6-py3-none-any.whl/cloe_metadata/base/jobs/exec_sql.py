from __future__ import annotations

import logging
import uuid
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators, writer

logger = logging.getLogger(__name__)


class Query(BaseModel):
    """Base class for loading query model objects."""

    exec_order: int = Field(..., description="Execution order of the query")
    query: str = Field(..., description="Query to be executed")
    description: str | None = Field(default=None, description="Description of the query.")
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)

    _check_query = field_validator("query")(validators.check_if_valid_template)


class ExecSQL(WithoutSubfoldersMixin):
    """Base class for loading ExecSQL model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(..., description="ID of the job")
    name: str = Field(..., description="Name of the job(must be unique)")
    description: str | None = Field(default=None, description="Description of the job.")
    connection_id: uuid.UUID = Field(
        ...,
        description="Reference the sink connection. Will later "
        "be used to establish a connection to the stored procedures database.",
    )
    queries: list[Query] = Field(..., description="All queries belonging to this job.")

    @field_validator("queries")
    @classmethod
    def runtimes_order_by_unique_check(cls, value: list[Query]):
        order_number = []
        for query in value:
            if query.exec_order not in order_number:
                order_number.append(query.exec_order)
            else:
                raise ValueError("Queries exec_order not unique")
        return value

    @classmethod
    def json_object_to_class(cls, data: dict) -> tuple[ExecSQL | None, list[ValidationError]]:
        errors = []
        queries = []
        for query in data.pop("queries", []):
            try:
                queries.append(Query(**query))
            except ValidationError as e:
                errors.append(e)
        try:
            instance = cls(**data, queries=queries)
        except ValidationError as e:
            instance = None
            errors.append(e)
        return instance, errors

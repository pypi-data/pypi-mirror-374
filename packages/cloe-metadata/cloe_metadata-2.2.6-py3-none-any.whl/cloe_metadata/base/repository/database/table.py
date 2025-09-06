from __future__ import annotations

import json
import logging
import pathlib
import uuid
from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, ValidationError, field_validator

from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.base.repository.database import column
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class Table(WithoutSubfoldersMixin):
    """Base class for loading Table model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(..., description="ID of the table")
    level: Literal["src", "stg", "ver", "core", "derived", "lu"] | None = Field(
        default=None, description="Level of the table"
    )
    name: str = Field(..., description="Name of the Table")
    columns: list[Annotated[column.Column, AfterValidator(validators.name_alphanumeric_table_columns)]] = []

    _check_name = field_validator("name")(validators.name_alphanumeric_table_name)

    @property
    def is_version(self) -> bool:
        return self.level == "ver"

    @classmethod
    def json_object_to_class(cls, data: dict) -> tuple[Table | None, list[ValidationError]]:
        errors = []
        columns = []
        for cm in data.pop("columns", []):
            try:
                columns.append(column.Column(**cm))
            except ValidationError as e:
                errors.append(e)
        try:
            instance = cls(**data, columns=columns)
        except ValidationError as e:
            instance = None
            errors.append(e)
        return instance, errors

    @classmethod
    def read_instances_from_disk(
        cls,
        input_path: pathlib.Path,
        fail_on_missing_subfolder: bool = True,  # noqa: ARG003
    ) -> tuple[list[Table], list[ValidationError | json.JSONDecodeError]]:
        stuff, errors = super().read_instances_from_disk(input_path, False)
        return super().read_instances_from_disk(input_path, False)

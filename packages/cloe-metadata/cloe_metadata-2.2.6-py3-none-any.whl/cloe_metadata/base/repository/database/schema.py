from __future__ import annotations

import json
import logging
import pathlib
import uuid
from typing import ClassVar

from pydantic import Field, ValidationError, field_validator

from cloe_metadata.base.base import WithSubfoldersMixin
from cloe_metadata.base.repository.database import table
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class Schema(WithSubfoldersMixin):
    """Base class for loading Schema model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("tables")
    exclude_when_writing_to_disk: ClassVar[set] = {"tables"}
    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="ID of the schema")
    name: str = Field(..., description="Name of the schema")
    tables: list[table.Table] = []

    @field_validator("tables")
    @classmethod
    def child_uniqueness_check(cls, value: list[table.Table]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def json_object_to_class(
        cls, data: dict, instance_dir: pathlib.Path
    ) -> tuple[Schema | None, list[ValidationError | json.JSONDecodeError]]:
        instance_folderpath = instance_dir / cls.subfolder_path
        tables, sub_errors = table.Table.read_instances_from_disk(instance_folderpath)
        try:
            instance = cls(**data, tables=tables)
        except ValidationError as e:
            instance = None
            sub_errors.append(e)
        return instance, sub_errors

    def _write_childs_to_disk(self, sub_output_path: pathlib.Path) -> None:
        for child in self.tables:
            child.write_to_disk(sub_output_path / self.subfolder_path)

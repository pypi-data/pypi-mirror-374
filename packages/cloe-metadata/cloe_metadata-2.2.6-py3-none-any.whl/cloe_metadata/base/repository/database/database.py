from __future__ import annotations

import json
import logging
import pathlib
import shutil
import uuid
from typing import ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)

from cloe_metadata.base.base import WithSubfoldersMixin
from cloe_metadata.base.repository.database import schema, table
from cloe_metadata.utils import validators, writer

logger = logging.getLogger(__name__)


class Database(WithSubfoldersMixin):
    """Base class for loading Database model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("schemas")
    exclude_when_writing_to_disk: ClassVar[set] = {"schemas"}
    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="ID of the database")
    display_name: str | None = Field(default=None, description="Display name of the database, mostly used for GUI.")
    name: str = Field(..., description="Technical name of the database")
    schemas: list[schema.Schema] = []

    _check_name_template = field_validator("name")(validators.check_if_valid_template)

    @field_validator("schemas")
    @classmethod
    def child_uniqueness_check(cls, value: list[schema.Schema]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def json_object_to_class(
        cls, data: dict, instance_dir: pathlib.Path
    ) -> tuple[Database | None, list[ValidationError | json.JSONDecodeError]]:
        instance_folderpath = instance_dir / cls.subfolder_path
        schemas, sub_errors = schema.Schema.read_instances_from_disk(
            instance_folderpath,
            fail_on_missing_subfolder=False,
        )
        try:
            instance = cls(**data, schemas=schemas)
        except ValidationError as e:
            instance = None
            sub_errors.append(e)
        return instance, sub_errors

    def _write_childs_to_disk(self, sub_output_path: pathlib.Path) -> None:
        for child in self.schemas:
            child.write_to_disk(sub_output_path / self.subfolder_path)


class Databases(BaseModel):
    """Base class for loading Databases model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("repository", "databases")

    databases: list[Database]
    _tables_cache: dict[uuid.UUID, table.Table] = {}
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)

    @field_validator("databases")
    @classmethod
    def child_uniqueness_check(cls, value: list[Database]):
        validators.find_non_unique(value, "name")
        return value

    @property
    def id_to_tables(self) -> dict[uuid.UUID, table.Table]:
        if len(self._tables_cache) < 1:
            self._tables_cache = {
                table.id: table for database in self.databases for schema in database.schemas for table in schema.tables
            }
        return self._tables_cache

    def get_table_and_schema(self, table_id: uuid.UUID) -> tuple[schema.Schema | None, table.Table | None]:
        for database in self.databases:
            for schema_obj in database.schemas:
                for table_obj in schema_obj.tables:
                    if table_obj.id == table_id:
                        return schema_obj, table_obj
        return None, None

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Databases, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = Database.read_instances_from_disk(input_path / cls.subfolder_path)
        try:
            instance = cls(databases=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path, delete_existing: bool = False) -> None:
        sub_output_path = output_path / self.subfolder_path
        if delete_existing and sub_output_path.exists() and sub_output_path.is_dir():
            shutil.rmtree(sub_output_path)
        for child in self.databases:
            child.write_to_disk(output_path / self.subfolder_path, delete_existing)

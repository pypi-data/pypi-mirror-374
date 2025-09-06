from __future__ import annotations

import json
import pathlib
import uuid
from typing import ClassVar, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)

import cloe_metadata.utils.writer as writer
from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators


class DataSourceInfo(WithoutSubfoldersMixin):
    """Base class for loading DataSourceInfo model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID
    name: str | None = None
    content: Literal["full", "delta"]
    sourcesystem_id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    object_description: str | None = None

    _check_name = field_validator("object_description")(validators.name_alphanumeric)


class DataSourceInfos(BaseModel):
    """Base class for loading DataSourceInfos model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path(
        "repository", "data_source_infos"
    )

    data_source_infos: list[DataSourceInfo] = Field(default=[])
    _data_source_infos_cache: dict[uuid.UUID, DataSourceInfo] = {}

    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("data_source_infos")
    @classmethod
    def child_uniqueness_check(cls, value: list[DataSourceInfo]):
        validators.find_non_unique(value, "object_description")
        return value

    def get_data_source_infos(self) -> dict[uuid.UUID, DataSourceInfo]:
        if len(self._data_source_infos_cache) < 1:
            self._data_source_infos_cache = {
                data_source_info.id: data_source_info
                for data_source_info in self.data_source_infos
            }
        return self._data_source_infos_cache

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[DataSourceInfos, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = DataSourceInfo.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(data_source_infos=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.data_source_infos:
            child.write_to_disk(output_path / self.subfolder_path)

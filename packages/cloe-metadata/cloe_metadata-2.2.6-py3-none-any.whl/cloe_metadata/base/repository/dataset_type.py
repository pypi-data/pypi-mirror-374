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


class DatasetType(WithoutSubfoldersMixin):
    """Base class for loading DatasetType model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID
    name: str
    storage_format: Literal["CSV", "Parquet"]
    attributes: list | None

    _check_name = field_validator("name")(validators.name_alphanumeric)

    @property
    def is_parquet(self) -> bool:
        return self.storage_format.lower() == "parquet"

    @property
    def is_csv(self) -> bool:
        return self.storage_format.lower() == "csv"


class DatasetTypes(BaseModel):
    """Base class for loading DatasetType model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("repository", "dataset_types")

    dataset_types: list[DatasetType] = Field(default=[])

    _dataset_types_cache: dict[uuid.UUID, DatasetType] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("dataset_types")
    @classmethod
    def child_uniqueness_check(cls, value: list[DatasetType]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[DatasetTypes, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = DatasetType.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(dataset_types=instances)
        except ValidationError as e:
            errors.append(e)
        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.dataset_types:
            child.write_to_disk(output_path / self.subfolder_path)

    def get_dataset_types(self) -> dict[uuid.UUID, DatasetType]:
        if len(self._dataset_types_cache) < 1:
            self._dataset_types_cache = {
                dataset_types.id: dataset_types for dataset_types in self.dataset_types
            }
        return self._dataset_types_cache

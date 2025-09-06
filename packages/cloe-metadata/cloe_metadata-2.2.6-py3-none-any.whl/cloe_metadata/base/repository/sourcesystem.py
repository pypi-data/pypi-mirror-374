from __future__ import annotations

import json
import pathlib
import uuid
from typing import ClassVar

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


class Sourcesystem(WithoutSubfoldersMixin):
    """Base class for loading Sourcesystem model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID
    name: str

    _check_name = field_validator("name")(validators.name_alphanumeric)


class Sourcesystems(BaseModel):
    """Base class for loading Sourcesystem model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("repository", "sourcesystems")

    sourcesystems: list[Sourcesystem] = Field(default=[])

    _sourcesystems_cache: dict[uuid.UUID, Sourcesystem] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("sourcesystems")
    @classmethod
    def child_uniqueness_check(cls, value: list[Sourcesystem]):
        validators.find_non_unique(value, "name")
        return value

    def get_sourcesystems(self) -> dict[uuid.UUID, Sourcesystem]:
        if len(self._sourcesystems_cache) < 1:
            self._sourcesystems_cache = {
                sourcesystems.id: sourcesystems for sourcesystems in self.sourcesystems
            }
        return self._sourcesystems_cache

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Sourcesystems, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = Sourcesystem.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(sourcesystems=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.sourcesystems:
            child.write_to_disk(output_path / self.subfolder_path)

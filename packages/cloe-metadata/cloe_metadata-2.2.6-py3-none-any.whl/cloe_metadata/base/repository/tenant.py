from __future__ import annotations

import json
import logging
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

logger = logging.getLogger(__name__)


class Tenant(WithoutSubfoldersMixin):
    """Base class for loading Tenant model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID
    name: str

    _check_name = field_validator("name")(validators.name_alphanumeric)


class Tenants(BaseModel):
    """Base class for loading Tenant model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("repository", "tenants")

    tenants: list[Tenant] = Field(default=[])

    _tenants_cache: dict[uuid.UUID, Tenant] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("tenants")
    @classmethod
    def child_uniqueness_check(cls, value: list[Tenant]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Tenants, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = Tenant.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(tenants=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.tenants:
            child.write_to_disk(output_path / self.subfolder_path)

    def get_tenants(self) -> dict[uuid.UUID, Tenant]:
        if len(self._tenants_cache) < 1:
            self._tenants_cache = {tenants.id: tenants for tenants in self.tenants}
        return self._tenants_cache

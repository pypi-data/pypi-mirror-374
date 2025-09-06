from __future__ import annotations

import json
import logging
import pathlib
from typing import ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    field_validator,
)

import cloe_metadata.utils.writer as writer
from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class SQLTemplate(WithoutSubfoldersMixin):
    """SQLTemplate metadata model base class"""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: int
    name: str
    template: str
    description: str | None = None

    _check_name = field_validator("name")(validators.name_alphanumeric)

    _check_template = field_validator("template")(validators.check_if_valid_template)


class SQLTemplates(BaseModel):
    """Base class for loading CLOE SQLTemplate model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path(
        "modeler", "templates", "sql_templates"
    )

    sql_templates: list[SQLTemplate] = []
    _sql_template_cache: dict[int, SQLTemplate] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("sql_templates")
    @classmethod
    def child_uniqueness_check(cls, value: list[SQLTemplate]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[SQLTemplates, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = SQLTemplate.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(sql_templates=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.sql_templates:
            child.write_to_disk(output_path / self.subfolder_path)

    def get_templates(self) -> dict[int, SQLTemplate]:
        if len(self._sql_template_cache) < 1:
            self._sql_template_cache = {
                template.id: template for template in self.sql_templates
            }
        return self._sql_template_cache

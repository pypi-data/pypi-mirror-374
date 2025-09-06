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


class DatatypeTemplate(WithoutSubfoldersMixin):
    """DatatypeTemplate metadata model base class"""

    attribute_used_for_filename: ClassVar[str] = "source_type"

    source_type: str
    parameter_template: str

    _check_name = field_validator("source_type")(validators.name_alphanumeric)

    _check_parameter_template = field_validator("parameter_template")(
        validators.check_if_valid_template
    )


class DatatypeTemplates(BaseModel):
    """Base class for loading CLOE DatatypeTemplate model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path(
        "modeler", "templates", "datatype_templates"
    )

    datatype_templates: list[DatatypeTemplate] = []
    _datatype_template_cache: dict[str, DatatypeTemplate] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("datatype_templates")
    @classmethod
    def child_uniqueness_check(cls, value: list[DatatypeTemplate]):
        validators.find_non_unique(value, "source_type")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[DatatypeTemplates, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = DatatypeTemplate.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(datatype_templates=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.datatype_templates:
            child.write_to_disk(output_path / self.subfolder_path)

    def get_templates(self) -> dict[str, DatatypeTemplate]:
        if len(self._datatype_template_cache) < 1:
            self._datatype_template_cache = {
                template.source_type: template for template in self.datatype_templates
            }
        return self._datatype_template_cache

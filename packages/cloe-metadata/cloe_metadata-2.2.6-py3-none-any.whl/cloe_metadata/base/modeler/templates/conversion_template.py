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


class ConversionTemplate(WithoutSubfoldersMixin):
    """ConversionTemplate metadata model base class"""

    attribute_used_for_filename: ClassVar[str] = "output_type"

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    output_type: str
    convert_template: str
    on_convert_error_default_value: str

    _check_name = field_validator("output_type")(validators.name_alphanumeric)

    _check_convert_template = field_validator("convert_template")(
        validators.check_if_valid_template
    )


class ConversionTemplates(BaseModel):
    """Base class for loading CLOE ConversionTemplate model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path(
        "modeler", "templates", "conversion_templates"
    )

    conversion_templates: list[ConversionTemplate] = []
    _conversion_template_cache: dict[str, ConversionTemplate] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("conversion_templates")
    @classmethod
    def child_uniqueness_check(cls, value: list[ConversionTemplate]):
        validators.find_non_unique(value, "output_type")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[ConversionTemplates, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = ConversionTemplate.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(conversion_templates=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.conversion_templates:
            child.write_to_disk(output_path / self.subfolder_path)

    def get_templates(self) -> dict[str, ConversionTemplate]:
        if len(self._conversion_template_cache) < 1:
            self._conversion_template_cache = {
                template.output_type: template for template in self.conversion_templates
            }
        return self._conversion_template_cache

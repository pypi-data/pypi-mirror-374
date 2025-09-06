import logging

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from cloe_metadata import base
from cloe_metadata.base.modeler.dataflow import column_mapping

logger = logging.getLogger(__name__)


class ColumnMapping(BaseModel):
    """Class for advanced or shared ColumnMapping functionality."""

    base_obj: column_mapping.ColumnMapping
    databases: base.Databases = Field(..., exclude=True)
    conversions: base.ConversionTemplates = Field(..., exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("databases")
    @classmethod
    def sink_table_exists(cls, value: base.Databases, info: ValidationInfo):
        """
        Validates that the sink table exists in the databases.

        Args:
            value (base.Databases): The databases object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If the sink_table_id does not exist in the databases.

        Returns:
            base.Databases: The validated databases object.
        """
        base_obj: column_mapping.ColumnMapping | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.sink_table_id not in value.id_to_tables:
            raise ValueError("sink_table_id does not exist")
        return value

    @field_validator("conversions")
    @classmethod
    def conversion_exists(cls, value: base.ConversionTemplates, info: ValidationInfo):
        """
        Validates that the conversion template exists in the conversion templates.

        Args:
            value (base.ConversionTemplates): The conversion templates object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If the convert_to_datatype does not exist in the conversion templates.

        Returns:
            base.ConversionTemplates: The validated conversion templates object.
        """
        base_obj: column_mapping.ColumnMapping | None = info.data.get("base_obj")
        if (
            base_obj is not None
            and base_obj.convert_to_datatype is not None
            and base_obj.convert_to_datatype not in value.get_templates()
        ):
            raise ValueError("convert_to_datatype does not exist")
        return value

    @property
    def sink_table(self) -> base.Table | None:
        """
        Returns the sink table object.

        Returns:
            base.Table | None: The sink table object, or None if it does not exist.
        """
        return self.databases.id_to_tables[self.base_obj.sink_table_id]

    @property
    def sink_schema_table(self) -> tuple[base.Schema | None, base.Table | None]:
        """
        Returns the sink schema and table objects.

        Returns:
            tuple[base.Schema | None, base.Table | None]: The sink schema
            and table objects, or None if they do not exist.
        """
        return self.databases.get_table_and_schema(self.base_obj.sink_table_id)

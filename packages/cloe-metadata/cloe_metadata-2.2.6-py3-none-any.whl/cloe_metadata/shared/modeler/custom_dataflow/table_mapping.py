import logging

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from cloe_metadata import base
from cloe_metadata.base.modeler.custom_dataflow import table_mapping

logger = logging.getLogger(__name__)


class TableMapping(BaseModel):
    """Class for advanced or shared TableMapping functionality."""

    base_obj: table_mapping.TableMapping
    databases: base.Databases = Field(..., exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("databases")
    @classmethod
    def sink_table_exists(cls, value: base.Databases, info: ValidationInfo):
        """
        Validates that the sink and source tables exist in the databases.

        Args:
            value (base.Databases): The databases object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If either the sink_table_id or source_table_id do not exist in the databases.

        Returns:
            base.Databases: The validated databases object.
        """
        base_obj: table_mapping.TableMapping | None = info.data.get("base_obj")
        error_text = ""
        if base_obj is not None and base_obj.sink_table_id not in value.id_to_tables:
            error_text += "sink_table_id "
        if base_obj is not None and base_obj.source_table_id not in value.id_to_tables:
            error_text += " source_table_id "
        if len(error_text) > 1:
            raise ValueError(f"{error_text} not in databases")
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
            tuple[base.Schema | None, base.Table | None]: The sink schema and table
            objects, or None if they do not exist.
        """
        return self.databases.get_table_and_schema(self.base_obj.sink_table_id)

    @property
    def source_table(self) -> base.Table | None:
        """
        Returns the source table object.

        Returns:
            base.Table | None: The source table object, or None if it does not exist.
        """
        return self.databases.id_to_tables[self.base_obj.source_table_id]

    @property
    def source_schema_table(self) -> tuple[base.Schema | None, base.Table | None]:
        """
        Returns the source schema and table objects.

        Returns:
            tuple[base.Schema | None, base.Table | None]: The source schema
            and table objects, or None if they do not exist.
        """
        return self.databases.get_table_and_schema(self.base_obj.source_table_id)

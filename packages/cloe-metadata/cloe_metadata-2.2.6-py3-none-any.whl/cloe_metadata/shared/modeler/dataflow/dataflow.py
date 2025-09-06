import logging

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from cloe_metadata import base
from cloe_metadata.shared.modeler.dataflow import column_mapping, lookup, source_table

logger = logging.getLogger(__name__)


class Dataflow(BaseModel):
    """Class for advanced or shared Dataflow functionality."""

    base_obj: base.Dataflow
    shared_lookups: list[lookup.Lookup]
    shared_source_tables: list[source_table.SourceTable]
    shared_column_mappings: list[column_mapping.ColumnMapping]
    databases: base.Databases = Field(..., exclude=True)
    sql_templates: base.SQLTemplates = Field(..., exclude=True)
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
        base_obj: base.Dataflow | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.sink_table_id not in value.id_to_tables:
            raise ValueError("sink_table_id does not exist")
        return value

    @field_validator("sql_templates")
    @classmethod
    def sql_template_exists(cls, value: base.SQLTemplates, info: ValidationInfo):
        """
        Validates that the SQL template exists in the SQL templates.

        Args:
            value (base.SQLTemplates): The SQL templates object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If the sql_template_id does not exist in the SQL templates.

        Returns:
            base.SQLTemplates: The validated SQL templates object.
        """
        base_obj: base.Dataflow | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.sql_template_id not in value.get_templates():
            raise ValueError("sql_template_id does not exist")
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
            tuple[base.Schema | None, base.Table | None]: The sink schema and
            table objects, or None if they do not exist.
        """
        return self.databases.get_table_and_schema(self.base_obj.sink_table_id)

    @property
    def sql_template(self) -> base.SQLTemplate | None:
        """
        Returns the SQL template object.

        Returns:
            base.SQLTemplate | None: The SQL template object, or None if it does not exist.
        """
        return self.sql_templates.get_templates().get(self.base_obj.sql_template_id)

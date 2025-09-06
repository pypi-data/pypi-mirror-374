import logging

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from cloe_metadata import base
from cloe_metadata.base.modeler.dataflow import lookup

logger = logging.getLogger(__name__)


class ReturnColumnMapping(BaseModel):
    """Class for advanced or shared ReturnColumnMapping functionality."""

    base_obj: lookup.ReturnColumnMapping
    databases: base.Databases = Field(..., exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("databases")
    @classmethod
    def tenant_exists(cls, value: base.Databases, info: ValidationInfo):
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
        base_obj: lookup.ReturnColumnMapping | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.sink_table_id not in value.id_to_tables:
            raise ValueError("sink_table_id does not exist")
        return value

    @property
    def sink_table(self) -> base.Table | None:
        """
        Returns the sink table object.

        Returns:
            base.Table | None: The sink table object, or None if it does not exist.
        """
        return self.databases.id_to_tables.get(self.base_obj.sink_table_id)

    @property
    def sink_schema_table(self) -> tuple[base.Schema | None, base.Table | None]:
        """
        Returns the sink schema and table objects.

        Returns:
            tuple[base.Schema | None, base.Table | None]: The sink schema
            and table objects, or None if they do not exist.
        """
        return self.databases.get_table_and_schema(self.base_obj.sink_table_id)


class Lookup(BaseModel):
    """Class for advanced or shared Lookup functionality."""

    base_obj: lookup.Lookup
    shared_return_column_mapping: list[ReturnColumnMapping]
    databases: base.Databases = Field(..., exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("databases")
    @classmethod
    def tenant_exists(cls, value: base.Databases, info: ValidationInfo):
        """
        Validates that the lookup table exists in the databases.

        Args:
            value (base.Databases): The databases object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If the lookup_table_id does not exist in the databases.

        Returns:
            base.Databases: The validated databases object.
        """
        base_obj: lookup.Lookup | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.lookup_table_id not in value.id_to_tables:
            raise ValueError("lookup_table_id does not exist")
        return value

    @property
    def source_table(self) -> base.Table | None:
        """
        Returns the source table object.

        Returns:
            base.Table | None: The source table object, or None if it does not exist.
        """
        return self.databases.id_to_tables.get(self.base_obj.lookup_table_id)

    @property
    def source_schema_table(self) -> tuple[base.Schema | None, base.Table | None]:
        """
        Returns the source schema and table objects.

        Returns:
            tuple[base.Schema | None, base.Table | None]: The source schema
            and table objects, or None if they do not exist.
        """
        return self.databases.get_table_and_schema(self.base_obj.lookup_table_id)

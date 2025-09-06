from __future__ import annotations

import logging
import uuid
from typing import Annotated, ClassVar

from pydantic import (
    AfterValidator,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)

import cloe_metadata.base.modeler.dataflow.lookup as lib_lookup
from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.base.modeler.dataflow import (
    column_mapping,
    source_table,
)
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


def lookup_parameters_order_by_unique_check(value: column_mapping.ColumnMapping, info: ValidationInfo):
    if (
        (
            info.data.get("include_dq1", True)
            or info.data.get("include_dq2", True)
            or info.data.get("include_dq3", False)
        )
        and value.calculation is not None
        and value.source_column_name is None
    ):
        raise ValueError("source_column_name must be set if calculation is used and dq is on")
    return value


class Dataflow(WithoutSubfoldersMixin):
    """Dataflow metadata model base class"""

    attribute_used_for_filename: ClassVar[str] = "name"

    name: str = Field(..., description="Name of the DataFlow(must be unique)")
    sink_table_id: uuid.UUID = Field(..., description="Reference to the sink table")
    sql_template_id: int = Field(..., description="Reference to sql template that should be used")
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="ID of the dataflow")
    job_id: uuid.UUID | None = Field(default=None, description="Reference to the sink Exec_SQL job")
    include_dq1: bool = Field(default=True, description="Use DQ1 features")
    column_mappings: list[
        Annotated[
            column_mapping.ColumnMapping,
            AfterValidator(lookup_parameters_order_by_unique_check),
        ]
    ]
    include_dq2: bool = Field(default=True, description="Use DQ2 features")
    include_dq3: bool = Field(default=False, description="Use DQ3 Features")
    log_dq1: bool = Field(default=True, description="Log DQ1 errors")
    log_dq2: bool = Field(default=True, description="Log DQ2 errors")
    log_dq3: bool = Field(default=False, description="Log DQ3 errors")
    source_tables: list[source_table.SourceTable]
    lookups: list[lib_lookup.Lookup] | None = Field(default=None)
    post_processing_sql: str | None = Field(default=None, description="Execute SQL query after Dataflow")
    pre_processing_sql: str | None = Field(default=None, description="Execute SQL query before Dataflow")

    _check_name_w_replace = field_validator("name")(validators.name_alphanumeric_w_replace)

    @field_validator("column_mappings")
    @classmethod
    def column_mapping_bk_check(cls, value: list[column_mapping.ColumnMapping]):
        if any(column_mapping.bk_order is not None for column_mapping in value):
            return value
        raise ValueError("no bk set.")

    @field_validator("include_dq2")
    @classmethod
    def dq2_and_conversion_check(cls, value: bool, info: ValidationInfo):
        column_mappings: list[column_mapping.ColumnMapping] = info.data.get("column_mappings", [])
        if len(column_mappings) > 0:
            if any(column_mapping.convert_to_datatype is not None for column_mapping in column_mappings):
                return value
            logger.warning("DQ2 activated but no conversions. Deactivating DQ2.")
            return False
        return value

    @field_validator("log_dq2")
    @classmethod
    def dq2_log_and_conversion_check(cls, value: bool, info: ValidationInfo):
        column_mappings: list[column_mapping.ColumnMapping] = info.data.get("column_mappings", [])
        if len(column_mappings) > 0:
            if any(column_mapping.is_logging_on_convert_error for column_mapping in column_mappings):
                return value
            logger.warning("DQ2 activated but no columns marked for logging." " Deactivating DQ2 logging.")
            return False
        return value

    @field_validator("source_tables")
    @classmethod
    def is_active_check(cls, value: list[source_table.SourceTable]):
        if all(not source_table.is_active for source_table in value):
            raise ValueError("at least one source table must be active.")
        return value

    @staticmethod
    def _read_lookup_instances(
        data: list[dict],
    ) -> tuple[list[lib_lookup.Lookup], list[ValidationError]]:
        instances = []
        errors = []
        for raw_lookup in data:
            try:
                lookup_parameters = [
                    lib_lookup.LookupParameter(**l_parameter) for l_parameter in raw_lookup.pop("lookupParameters", [])
                ]
                return_column_mapping = [
                    lib_lookup.ReturnColumnMapping(**l_rcm) for l_rcm in raw_lookup.pop("returnColumnMappings", [])
                ]
                lookup = lib_lookup.Lookup(
                    **raw_lookup,
                    lookup_parameters=lookup_parameters,
                    return_column_mappings=return_column_mapping,
                )
                instances.append(lookup)
            except ValidationError as e:
                errors.append(e)
        return instances, errors

    @staticmethod
    def _read_source_table_instances(
        data: list[dict],
    ) -> tuple[list[source_table.SourceTable], list[ValidationError]]:
        instances = []
        errors = []
        for st in data:
            try:
                instances.append(source_table.SourceTable(**st))
            except ValidationError as e:
                errors.append(e)
        return instances, errors

    @staticmethod
    def _read_column_mapping_instances(
        data: list[dict],
    ) -> tuple[list[column_mapping.ColumnMapping], list[ValidationError]]:
        instances = []
        errors = []
        for cm in data:
            try:
                instances.append(column_mapping.ColumnMapping(**cm))
            except ValidationError as e:
                errors.append(e)
        return instances, errors

    @classmethod
    def json_object_to_class(cls, data: dict) -> tuple[Dataflow | None, list[ValidationError]]:
        errors = []
        lookups, l_errors = cls._read_lookup_instances(data.pop("lookups", []))
        errors += l_errors
        source_tables, st_errors = cls._read_source_table_instances(data.pop("tableMappings", []))
        errors += st_errors
        column_mappings, cm_errors = cls._read_column_mapping_instances(data.pop("columnMappings", []))
        errors += cm_errors
        try:
            instance = cls(
                **data,
                source_tables=source_tables,
                column_mappings=column_mappings,
                lookups=lookups,
            )
        except ValidationError as e:
            instance = None
            errors.append(e)
        return instance, errors

import uuid

from pydantic import ValidationError

from cloe_metadata import base
from cloe_metadata.base.modeler.dataflow import column_mapping, lookup, source_table
from cloe_metadata.shared.modeler import dataflow


def transform_power_pipe_column_mappings_to_shared(
    base_obj_collection: list[column_mapping.ColumnMapping],
    databases: base.Databases,
    conversions: base.ConversionTemplates,
) -> tuple[list[dataflow.ColumnMapping], list[ValidationError]]:
    errors: list[ValidationError] = []
    shared_obj_collection = []
    for base_obj in base_obj_collection:
        try:
            shared_obj = dataflow.ColumnMapping(
                base_obj=base_obj, databases=databases, conversions=conversions
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            errors.append(err)
    return shared_obj_collection, errors


def transform_power_pipe_lookup_return_column_mappings_to_shared(
    base_obj_collection: list[lookup.ReturnColumnMapping],
    databases: base.Databases,
) -> tuple[list[dataflow.ReturnColumnMapping], list[ValidationError]]:
    errors: list[ValidationError] = []
    shared_obj_collection = []
    for base_obj in base_obj_collection:
        try:
            shared_obj = dataflow.ReturnColumnMapping(
                base_obj=base_obj, databases=databases
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            errors.append(err)
    return shared_obj_collection, errors


def transform_power_pipe_lookups_to_shared(
    base_obj_collection: list[lookup.Lookup],
    databases: base.Databases,
) -> tuple[list[dataflow.Lookup], list[ValidationError]]:
    errors: list[ValidationError] = []
    shared_obj_collection = []
    for base_obj in base_obj_collection:
        try:
            (
                shared_return_column_mapping,
                shared_rcm_errors,
            ) = transform_power_pipe_lookup_return_column_mappings_to_shared(
                base_obj_collection=base_obj.return_column_mappings,
                databases=databases,
            )
            errors += shared_rcm_errors
            shared_obj = dataflow.Lookup(
                base_obj=base_obj,
                shared_return_column_mapping=shared_return_column_mapping,
                databases=databases,
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            errors.append(err)
    return shared_obj_collection, errors


def transform_power_pipe_source_tables_to_shared(
    base_obj_collection: list[source_table.SourceTable],
    databases: base.Databases,
    tenants: base.Tenants,
) -> tuple[list[dataflow.SourceTable], list[ValidationError]]:
    errors: list[ValidationError] = []
    shared_obj_collection = []
    for base_obj in base_obj_collection:
        try:
            shared_obj = dataflow.SourceTable(
                base_obj=base_obj, databases=databases, tenants=tenants
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            errors.append(err)
    return shared_obj_collection, errors


def transform_power_pipes_to_shared(
    base_obj_collection: base.Flows,
    databases: base.Databases,
    tenants: base.Tenants,
    conversion_templates: base.ConversionTemplates,
    sql_templates: base.SQLTemplates,
) -> tuple[list[dataflow.Dataflow], dict[uuid.UUID, list[ValidationError]]]:
    errors: dict[uuid.UUID, list[ValidationError]] = {}
    shared_obj_collection = []
    for base_obj in base_obj_collection.get_dataflows():
        pipe_error = []
        try:
            (
                shared_column_mappings,
                shared_cm_errors,
            ) = transform_power_pipe_column_mappings_to_shared(
                base_obj_collection=base_obj.column_mappings,
                databases=databases,
                conversions=conversion_templates,
            )
            pipe_error += shared_cm_errors
            (
                shared_source_tables,
                shared_st_errors,
            ) = transform_power_pipe_source_tables_to_shared(
                base_obj_collection=base_obj.source_tables,
                databases=databases,
                tenants=tenants,
            )
            pipe_error += shared_st_errors
            (
                shared_lookups,
                shared_lu_errors,
            ) = transform_power_pipe_lookups_to_shared(
                base_obj_collection=base_obj.lookups or [],
                databases=databases,
            )
            pipe_error += shared_lu_errors
            shared_obj = dataflow.Dataflow(
                base_obj=base_obj,
                shared_column_mappings=shared_column_mappings,
                shared_source_tables=shared_source_tables,
                shared_lookups=shared_lookups,
                databases=databases,
                sql_templates=sql_templates,
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            pipe_error.append(err)
            errors[base_obj.id] = pipe_error
    return shared_obj_collection, errors

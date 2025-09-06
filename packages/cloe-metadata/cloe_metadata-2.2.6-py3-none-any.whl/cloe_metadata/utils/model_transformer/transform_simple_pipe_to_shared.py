import uuid

from pydantic import ValidationError

from cloe_metadata import base
from cloe_metadata.base.modeler.custom_dataflow import table_mapping
from cloe_metadata.shared.modeler import custom_dataflow


def transform_simple_pipe_table_mappings_to_shared(
    base_obj_collection: list[table_mapping.TableMapping],
    databases: base.Databases,
) -> tuple[list[custom_dataflow.TableMapping], list[ValidationError]]:
    errors: list[ValidationError] = []
    shared_obj_collection = []
    for base_obj in base_obj_collection:
        try:
            shared_obj = custom_dataflow.TableMapping(
                base_obj=base_obj, databases=databases
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            errors.append(err)
    return shared_obj_collection, errors


def transform_simple_pipes_to_shared(
    base_obj_collection: base.Flows,
    databases: base.Databases,
) -> tuple[
    list[custom_dataflow.CustomDataflow], dict[uuid.UUID, list[ValidationError]]
]:
    errors: dict[uuid.UUID, list[ValidationError]] = {}
    shared_obj_collection = []
    for base_obj in base_obj_collection.get_custom_dataflows():
        pipe_error = []
        try:
            (
                shared_table_mappings,
                shared_tm_errors,
            ) = transform_simple_pipe_table_mappings_to_shared(
                base_obj_collection=base_obj.table_mappings,
                databases=databases,
            )
            pipe_error += shared_tm_errors
            shared_obj = custom_dataflow.CustomDataflow(
                base_obj=base_obj,
                shared_table_mappings=shared_table_mappings,
            )
            shared_obj_collection.append(shared_obj)
        except ValidationError as err:
            pipe_error.append(err)
            errors[base_obj.id] = pipe_error
    return shared_obj_collection, errors

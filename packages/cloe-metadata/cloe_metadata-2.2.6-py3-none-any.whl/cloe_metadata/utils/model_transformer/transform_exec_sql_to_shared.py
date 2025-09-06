import uuid

from pydantic import ValidationError

from cloe_metadata import base
from cloe_metadata.shared import jobs


def transform_exec_sql_to_shared(
    base_obj_collection: base.Jobs,
    connections: base.Connections,
) -> tuple[dict[uuid.UUID, jobs.ExecSQL], dict[uuid.UUID, list[ValidationError]]]:
    errors: dict[uuid.UUID, list[ValidationError]] = {}
    shared_obj_collection = {}
    for base_obj in base_obj_collection.get_exec_sql_jobs():
        try:
            shared_obj = jobs.ExecSQL(
                base_obj=base_obj,
                connections=connections,
            )
            shared_obj_collection[base_obj.id] = shared_obj
        except ValidationError as err:
            errors[base_obj.id] = [err]
    return shared_obj_collection, errors

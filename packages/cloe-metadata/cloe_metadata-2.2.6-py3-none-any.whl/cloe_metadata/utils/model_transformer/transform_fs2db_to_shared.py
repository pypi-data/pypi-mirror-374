import uuid

from pydantic import ValidationError

from cloe_metadata import base
from cloe_metadata.shared import jobs


def transform_fs2db_to_shared(
    base_obj_collection: base.Jobs,
    dataset_types: base.DatasetTypes,
    databases: base.Databases,
    exec_sqls: dict[uuid.UUID, jobs.ExecSQL],
    connections: base.Connections,
) -> tuple[dict[uuid.UUID, jobs.FS2DB], dict[uuid.UUID, list[ValidationError]]]:
    errors: dict[uuid.UUID, list[ValidationError]] = {}
    shared_obj_collection = {}
    for base_obj in base_obj_collection.get_fs2db_jobs():
        try:
            shared_obj = jobs.FS2DB(
                base_obj=base_obj,
                dataset_types=dataset_types,
                databases=databases,
                connections=connections,
                exec_sqls=exec_sqls,
            )
            shared_obj_collection[base_obj.id] = shared_obj
        except ValidationError as err:
            errors[base_obj.id] = [err]
    return shared_obj_collection, errors

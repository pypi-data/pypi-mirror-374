import uuid

from pydantic import ValidationError

from cloe_metadata import base
from cloe_metadata.shared import jobs, repository


def transform_db2fs_to_shared(
    base_obj_collection: base.Jobs,
    dataset_types: base.DatasetTypes,
    databases: base.Databases,
    data_source_infos: dict[uuid.UUID, repository.DataSourceInfo],
    connections: base.Connections,
) -> tuple[dict[uuid.UUID, jobs.DB2FS], dict[uuid.UUID, list[ValidationError]]]:
    errors: dict[uuid.UUID, list[ValidationError]] = {}
    shared_obj_collection = {}
    for base_obj in base_obj_collection.get_db2fs_jobs():
        try:
            shared_obj = jobs.DB2FS(
                base_obj=base_obj,
                dataset_types=dataset_types,
                databases=databases,
                data_source_infos=data_source_infos,
                connections=connections,
            )
            shared_obj_collection[base_obj.id] = shared_obj
        except ValidationError as err:
            errors[base_obj.id] = [err]
    return shared_obj_collection, errors

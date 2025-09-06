import uuid

from pydantic import ValidationError

from cloe_metadata import base
from cloe_metadata.shared import repository


def transform_data_source_info_to_shared(
    base_obj_collection: base.DataSourceInfos,
    sourcesystems: base.Sourcesystems,
    tenants: base.Tenants,
) -> tuple[
    dict[uuid.UUID, repository.DataSourceInfo], dict[uuid.UUID, list[ValidationError]]
]:
    errors: dict[uuid.UUID, list[ValidationError]] = {}
    shared_obj_collection = {}
    for base_obj in base_obj_collection.data_source_infos:
        try:
            shared_obj = repository.DataSourceInfo(
                base_obj=base_obj, sourcesystems=sourcesystems, tenants=tenants
            )
            shared_obj_collection[base_obj.id] = shared_obj
        except ValidationError as err:
            errors[base_obj.id] = [err]
    return shared_obj_collection, errors

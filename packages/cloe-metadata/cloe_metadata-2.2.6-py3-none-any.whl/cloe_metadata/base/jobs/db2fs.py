from __future__ import annotations

import logging
import uuid
from typing import ClassVar

from pydantic import Field, field_validator

from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class DB2FS(WithoutSubfoldersMixin):
    """Base class for loading DB2FS model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(..., description="ID of the job")
    name: str = Field(..., description="Name of the job(must be unique)")
    description: str | None = Field(default=None, description="Description of the job.")
    sink_connection_id: uuid.UUID = Field(
        ...,
        description="Reference the sink connection. Will be used to establish a connection to the bucket/blob.",
    )
    source_connection_id: uuid.UUID = Field(
        ...,
        description="Reference the sink connection. Will be used to establish a connection to the database.",
    )
    container_name: str = Field(..., description="Name of the bucket/blob where the file is saved to.")
    select_statement: str = Field(
        ...,
        description="This query is executed and its result set stored in the file. Jinja2 templating is supported.",
    )
    dataset_type_id: uuid.UUID = Field(
        ...,
        description="Reference a datasettype which is partly used to "
        "generate the filename and to define the target filetype(e.g. Parquet).",
    )
    source_table_id: uuid.UUID = Field(
        ...,
        description="Reference a table. Table metadata e.g. its Name or "
        "table column names can be used in the Source_SelectStatement.",
    )
    datasource_info_id: uuid.UUID = Field(
        ...,
        description="Reference a datasourceinfo which is partly used to generate the filename.",
    )
    folder_path: str | None = Field(default=None, description="Path where the file will be saved to.")
    sequence_column_name: str | None = Field(default=None, description="Currently not supported")

    _check_name_w_replace = field_validator("name")(validators.name_alphanumeric_w_replace)

    _check_select_statement = field_validator("select_statement")(validators.check_if_valid_template)

    _check_folder_path = field_validator("folder_path")(validators.check_if_valid_template)

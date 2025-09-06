from __future__ import annotations

import logging
import uuid
from typing import ClassVar

from pydantic import Field, field_validator

from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class FS2DB(WithoutSubfoldersMixin):
    """Base class for loading FS2DB model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(..., description="ID of the job")
    name: str = Field(..., description="Name of the job(must be unique)")
    description: str | None = Field(default=None, description="Description of the job.")
    sink_connection_id: uuid.UUID = Field(
        ...,
        description="Reference the sink connection. Will be used to establish a connection to the database.",
    )
    source_connection_id: uuid.UUID = Field(
        ...,
        description="Reference the sink connection. Will be used to establish a connection to the bucket/blob.",
    )
    container_name: str = Field(..., description="Name of the bucket/blob where the file are located.")
    filename_pattern: str = Field(
        ...,
        description="Pattern by which the filenames on Blob/Bucket or FileCatalog should be filtered.",
    )
    folder_path_pattern: str = Field(
        ...,
        description="Pattern by which the path on Blob/Bucket or FileCatalog should be filtered..",
    )
    sink_table_id: uuid.UUID = Field(..., description="Reference to the sink table where data should be loaded to.")
    dataset_type_id: uuid.UUID = Field(
        ...,
        description="Reference a datasettype which is partly used to generate "
        "the filename and to define the target filetype(e.g. Parquet).",
    )
    get_from_filecatalog: bool = Field(
        default=False,
        description="If a filecatalog is used to corrdinator file loading.",
    )
    post_load_exec_job_id: uuid.UUID | None = Field(
        default=None,
        description="Exec Job to be executed after successful loading a file.",
    )

    _check_filename_pattern = field_validator("filename_pattern")(validators.check_if_valid_template)

    _check_folder_path_pattern = field_validator("folder_path_pattern")(validators.check_if_valid_template)

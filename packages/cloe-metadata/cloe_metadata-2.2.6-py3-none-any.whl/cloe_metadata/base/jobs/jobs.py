from __future__ import annotations

import json
import logging
import pathlib
import uuid
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

import cloe_metadata.utils.writer as writer
from cloe_metadata.base.jobs import DB2FS, FS2DB, ExecSQL
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class Jobs(BaseModel):
    """Base class for loading Job model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("jobs")
    child_to_folder_name: ClassVar[dict[str, str]] = {
        DB2FS.__name__: "db2fs",
        FS2DB.__name__: "fs2db",
        ExecSQL.__name__: "execsql",
    }

    jobs: list[DB2FS | FS2DB | ExecSQL] = Field(default=[])
    _jobs_cache: dict[uuid.UUID, DB2FS | FS2DB | ExecSQL] = {}
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

    @field_validator("jobs")
    @classmethod
    def child_uniqueness_check(cls, value: list[DB2FS | FS2DB | ExecSQL]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Jobs, list[ValidationError | json.JSONDecodeError]]:
        instances: list[DB2FS | FS2DB | ExecSQL] = []
        errors = []
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances_path = input_path / cls.subfolder_path
        sub_jobs: list[type[DB2FS] | type[FS2DB] | type[ExecSQL]] = [
            DB2FS,
            FS2DB,
            ExecSQL,
        ]
        for sub_job in sub_jobs:
            sub_instances, sub_errors = sub_job.read_instances_from_disk(
                instances_path / cls.child_to_folder_name[sub_job.__name__]
            )
            instances += sub_instances
            errors += sub_errors
        try:
            instance = cls(jobs=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.jobs:
            child.write_to_disk(
                output_path
                / self.subfolder_path
                / self.child_to_folder_name[child.__class__.__name__]
            )

    def get_jobs(self) -> dict[uuid.UUID, DB2FS | FS2DB | ExecSQL]:
        if len(self._jobs_cache) < 1:
            self._jobs_cache = {jobs.id: jobs for jobs in self.jobs}
        return self._jobs_cache

    def get_db2fs_jobs(
        self,
    ) -> list[DB2FS]:
        """
        Filters the jobs list

        :return: List of jobs of the specified type
        """
        return [job for job in self.jobs if isinstance(job, DB2FS)]

    def get_fs2db_jobs(
        self,
    ) -> list[FS2DB]:
        """
        Filters the jobs list

        :return: List of jobs of the specified type
        """
        return [job for job in self.jobs if isinstance(job, FS2DB)]

    def get_exec_sql_jobs(
        self,
    ) -> list[ExecSQL]:
        """
        Filters the jobs list

        :return: List of jobs of the specified type
        """
        return [job for job in self.jobs if isinstance(job, ExecSQL)]

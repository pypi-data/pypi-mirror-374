from __future__ import annotations

import json
import pathlib
import uuid
from typing import ClassVar

from croniter import croniter
from pydantic import BaseModel, Field, ValidationError, field_validator

from cloe_metadata.base.base import WithSubfoldersMixin
from cloe_metadata.base.batch.batchstep import Batchstep
from cloe_metadata.utils import validators


class Batch(WithSubfoldersMixin):
    """Base class for loading Batch model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("batchsteps")
    exclude_when_writing_to_disk: ClassVar[set] = {"batchsteps"}
    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(
        title="Batch ID",
        default_factory=uuid.uuid4,
        description="The batch ID so that it can referenced.",
    )
    name: str = Field(..., description="Name of the Batch(must be unique)")
    cron: str = Field(..., description="Cron schedule for batch scheduling.")
    batchsteps: list[Batchstep] = Field(
        ..., description="A list of all batchsteps belonging to that batch."
    )
    timezone: str = Field(..., description="Timezone for cron")
    tags: str | None = Field(default=None, description="Tags of the Batch")
    _batchsteps_cache: dict[uuid.UUID, Batchstep] = {}

    _check_name_w_replace = field_validator("name")(
        validators.name_alphanumeric_w_replace
    )

    @field_validator("cron")
    @classmethod
    def cron_valid_check(cls, value):
        if not croniter.is_valid(value):
            raise ValueError("is not a valid cron")
        return value

    @field_validator("batchsteps")
    @classmethod
    def child_uniqueness_check(cls, value):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def json_object_to_class(
        cls, data: dict, instance_dir: pathlib.Path
    ) -> tuple[Batch | None, list[ValidationError | json.JSONDecodeError]]:
        instance_folderpath = instance_dir / cls.subfolder_path
        batchsteps, sub_errors = Batchstep.read_instances_from_disk(instance_folderpath)
        try:
            instance = cls(**data, batchsteps=batchsteps)
        except ValidationError as e:
            instance = None
            sub_errors.append(e)
        return instance, sub_errors

    def _write_childs_to_disk(self, sub_output_path: pathlib.Path) -> None:
        for child in self.batchsteps:
            child.write_to_disk(sub_output_path / self.subfolder_path)

    def get_batchsteps(self) -> dict[uuid.UUID, Batchstep]:
        if len(self._batchsteps_cache) < 1:
            self._batchsteps_cache = {jobs.id: jobs for jobs in self.batchsteps}
        return self._batchsteps_cache


class Batches(BaseModel):
    """Base class for loading Batch model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("orchestration", "batches")

    batches: list[Batch] = []

    @field_validator("batches")
    @classmethod
    def child_uniqueness_check(cls, value: list[Batch]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Batches, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")
        instances, errors = Batch.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(batches=instances)
        except ValidationError as e:
            errors.append(e)
        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.batches:
            child.write_to_disk(output_path / self.subfolder_path)

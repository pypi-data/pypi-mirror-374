from __future__ import annotations

import uuid
from typing import Annotated, ClassVar

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)

import cloe_metadata.utils.writer as writer
from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators


def dependencies_self_dependency(value: BatchstepDependency, info: ValidationInfo):
    id: uuid.UUID = info.data.get("id", uuid.UUID(int=0))
    if value.dependent_on_batchstep_id == id:
        raise ValueError("must not have a dependency on itself")
    return value


class BatchstepDependency(BaseModel):
    """Base class for loading BatchstepDependency model objects."""

    dependent_on_batchstep_id: uuid.UUID = Field(..., description="Reference to a Batchstep this Batchstep depdends on")
    ignore_dependency_failed_state: bool = Field(
        ..., description="If dependency fails should Batchstep still be executed?"
    )

    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)


class Batchstep(WithoutSubfoldersMixin):
    """Base class for loading Batchstep model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    id: uuid.UUID = Field(..., description="UUID of the Batchstep")
    name: str = Field(..., description="Name of the Batchstep(must be unique)")
    job_id: uuid.UUID = Field(..., description="Reference to a job")
    tags: str | None = Field(default=None, description="Tags of the Batchstep")
    dependencies: list[Annotated[BatchstepDependency, AfterValidator(dependencies_self_dependency)]] | None = Field(
        default=None, description="All dependencies belonging to that job."
    )

    _check_name_w_replace = field_validator("name")(validators.name_alphanumeric_w_replace)

    @classmethod
    def json_object_to_class(cls, data: dict) -> tuple[Batchstep | None, list[ValidationError]]:
        errors = []
        dependencies = []
        for dependency in data.pop("dependencies", []):
            try:
                dependencies.append(BatchstepDependency(**dependency))
            except ValidationError as e:
                errors.append(e)
        try:
            instance = cls(**data, dependencies=dependencies)
        except ValidationError as e:
            instance = None
            errors.append(e)
        return instance, errors

    def get_dependencies(self) -> list[uuid.UUID]:
        if self.dependencies is None:
            return []
        return [i.dependent_on_batchstep_id for i in self.dependencies]

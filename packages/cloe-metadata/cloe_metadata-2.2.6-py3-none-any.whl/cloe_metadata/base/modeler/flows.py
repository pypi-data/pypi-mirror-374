from __future__ import annotations

import json
import logging
import pathlib
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

import cloe_metadata.utils.writer as writer
from cloe_metadata.base.modeler import custom_dataflow, dataflow
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class Flows(BaseModel):
    """Base class for loading CLOE Pipe model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("modeler")
    child_to_folder_name: ClassVar[dict[str, str]] = {
        dataflow.Dataflow.__name__: "dataflows",
        custom_dataflow.CustomDataflow.__name__: "custom_dataflows",
    }

    dataflows: list[custom_dataflow.CustomDataflow | dataflow.Dataflow] = Field(
        default=[]
    )
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )

    @field_validator("dataflows")
    @classmethod
    def child_uniqueness_check(
        cls, value: list[custom_dataflow.CustomDataflow | dataflow.Dataflow]
    ):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Flows, list[ValidationError | json.JSONDecodeError]]:
        instances: list[custom_dataflow.CustomDataflow | dataflow.Dataflow] = []
        errors = []
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances_path = input_path / cls.subfolder_path
        sub_pipes: list[
            type[custom_dataflow.CustomDataflow] | type[dataflow.Dataflow]
        ] = [
            custom_dataflow.CustomDataflow,
            dataflow.Dataflow,
        ]
        for sub_pipe in sub_pipes:
            sub_instances, sub_errors = sub_pipe.read_instances_from_disk(
                instances_path / cls.child_to_folder_name[sub_pipe.__name__]
            )
            instances += sub_instances
            errors += sub_errors
        try:
            instance = cls(dataflows=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.dataflows:
            child.write_to_disk(
                output_path
                / self.subfolder_path
                / self.child_to_folder_name[child.__class__.__name__]
            )

    def get_dataflows(
        self,
    ) -> list[dataflow.Dataflow]:
        """
        Filters the pipes list based on the given pipe type.
        """
        return [pipe for pipe in self.dataflows if isinstance(pipe, dataflow.Dataflow)]

    def get_custom_dataflows(
        self,
    ) -> list[custom_dataflow.CustomDataflow]:
        """
        Filters the pipes list based on the given pipe type.
        """
        return [
            pipe
            for pipe in self.dataflows
            if isinstance(pipe, custom_dataflow.CustomDataflow)
        ]

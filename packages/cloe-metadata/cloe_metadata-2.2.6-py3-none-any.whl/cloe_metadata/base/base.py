from __future__ import annotations

import json
import pathlib
import shutil
from typing import ClassVar

import typing_extensions
from pydantic import BaseModel, ConfigDict, ValidationError

import cloe_metadata.utils.writer as writer


class WithoutSubfoldersMixin(BaseModel):
    """
    Base class for all read/write methods of metadata classes that either
    have no children or write children metadata to their own metadata file.
    """

    attribute_used_for_filename: ClassVar[str] = ""
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)

    @classmethod
    def json_object_to_class(cls, data: dict) -> tuple[typing_extensions.Self | None, list[ValidationError]]:
        errors = []
        try:
            instance = cls(**data)
        except ValidationError as e:
            instance = None
            errors.append(e)
        return instance, errors

    @classmethod
    def _read_from_file(
        cls, instance_path: pathlib.Path
    ) -> tuple[typing_extensions.Self | None, list[ValidationError | json.JSONDecodeError]]:
        errors: list[ValidationError | json.JSONDecodeError] = []
        try:
            with instance_path.open("r") as file:
                data = json.load(file)
                instance, sub_errors = cls.json_object_to_class(data)
                errors += sub_errors
        except (ValidationError, json.JSONDecodeError) as e:
            instance = None
            errors.append(e)
        return instance, errors

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path, fail_on_missing_subfolder: bool = True
    ) -> tuple[list[typing_extensions.Self], list[ValidationError | json.JSONDecodeError]]:
        instances: list[typing_extensions.Self] = []
        errors: list[ValidationError | json.JSONDecodeError] = []

        if not input_path.exists() or not input_path.is_dir():
            if fail_on_missing_subfolder:
                raise FileNotFoundError(f"Directory not found: {input_path}")
            return instances, errors

        for instance_file in input_path.iterdir():
            sub_errors: list[ValidationError | json.JSONDecodeError] = []
            if instance_file.is_file() and instance_file.suffix == ".json":
                instance, sub_errors = cls._read_from_file(instance_file)
                instances += [] if instance is None else [instance]
            errors += sub_errors

        return instances, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        sub_output_path = output_path
        content = self.model_dump_json(
            indent=4,
            by_alias=True,
            exclude_none=True,
        )
        writer.write_string_to_disk(
            content,
            sub_output_path / f"{self.__getattribute__(self.attribute_used_for_filename)}.json",
        )


class WithSubfoldersMixin(BaseModel):
    """
    Base class for all read/write methods of metadata classes that have
    children and write/read them to/from separate files.
    """

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path()
    exclude_when_writing_to_disk: ClassVar[set] = set()
    attribute_used_for_filename: ClassVar[str] = ""
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)

    @classmethod
    def json_object_to_class(
        cls,
        data: dict,
        instance_dir: pathlib.Path,  # noqa: ARG003
    ) -> tuple[typing_extensions.Self | None, list[ValidationError | json.JSONDecodeError]]:
        errors = []
        try:
            instance = cls(**data)
        except (ValidationError, json.JSONDecodeError) as e:
            instance = None
            errors.append(e)
        return instance, errors

    @classmethod
    def _read_from_folder(
        cls, instance_path: pathlib.Path
    ) -> tuple[typing_extensions.Self | None, list[ValidationError | json.JSONDecodeError]]:
        errors: list[ValidationError | json.JSONDecodeError] = []
        json_files = list(instance_path.glob("*.json"))
        if json_files:
            json_file = json_files[0]
            try:
                with json_file.open("r") as file:
                    data = json.load(file)
                    instance, sub_errors = cls.json_object_to_class(data, instance_path)
                    errors += sub_errors
            except (ValidationError, json.JSONDecodeError) as e:
                instance = None
                errors.append(e)
                errors += sub_errors
        else:
            raise FileNotFoundError(f"No JSON file found in directory: {instance_path}")
        return instance, errors

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path, fail_on_missing_subfolder: bool = True
    ) -> tuple[list[typing_extensions.Self], list[ValidationError | json.JSONDecodeError]]:
        instances: list[typing_extensions.Self] = []
        errors: list[ValidationError | json.JSONDecodeError] = []

        if not input_path.exists() or not input_path.is_dir():
            if fail_on_missing_subfolder:
                raise FileNotFoundError(f"Directory not found: {input_path}")
            return instances, errors

        for instance_dir in input_path.iterdir():
            if instance_dir.is_dir():
                instance, sub_errors = cls._read_from_folder(instance_dir)
            instances += [] if instance is None else [instance]
            errors += sub_errors

        return instances, errors

    def _write_childs_to_disk(self, sub_output_path: pathlib.Path) -> None:
        pass

    def write_to_disk(self, output_path: pathlib.Path, delete_existing: bool = False) -> None:
        sub_output_path = output_path
        sub_output_path = output_path / f"{self.__getattribute__(self.attribute_used_for_filename)}"
        if delete_existing and sub_output_path.exists() and sub_output_path.is_dir():
            shutil.rmtree(sub_output_path)
        self._write_childs_to_disk(sub_output_path)
        content = self.model_dump_json(
            indent=4,
            by_alias=True,
            exclude_none=True,
            exclude=self.exclude_when_writing_to_disk,
        )
        writer.write_string_to_disk(
            content,
            sub_output_path / f"{self.__getattribute__(self.attribute_used_for_filename)}.json",
        )

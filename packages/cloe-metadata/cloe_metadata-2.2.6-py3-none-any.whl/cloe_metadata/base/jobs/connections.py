from __future__ import annotations

import json
import logging
import pathlib
import uuid
from typing import ClassVar

from pydantic import BaseModel, Field, ValidationError, field_validator

from cloe_metadata.base.base import WithoutSubfoldersMixin
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class Connection(WithoutSubfoldersMixin):
    """Base class for loading Connection model objects."""

    attribute_used_for_filename: ClassVar[str] = "name"

    azure_synapse_key: ClassVar[str] = "Azure Synapse Analytics"
    sql_server_nativ_key: ClassVar[str] = "SQL Server >=2016"
    azure_server_nativ_key: ClassVar[str] = "Azure SQL Server"
    snowflake_nativ_key: ClassVar[str] = "Snowflake"
    azure_blob_key: ClassVar[str] = "AzureBlob"
    oracle_key: ClassVar[str] = "Oracle"
    db2_key: ClassVar[str] = "DB2"
    postgresql_key: ClassVar[str] = "PostgreSQL"
    azurepostgresql_key: ClassVar[str] = "AzurePostgreSQL"

    connection_string_secret_name: str = Field(
        ...,
        description="Name of the secret that holds the connection information(e.g. password or host)",
    )
    id: uuid.UUID = Field(..., description="UUID of the connection")
    name: str = Field(..., description="Name of the connection(must be unique)")
    system_type: str = Field(..., description="Connection type")
    service_level: str | None = Field(
        default=None, description="service level of the connection"
    )
    is_file_catalog_connection: bool = Field(
        default=False, description="Can the FileCatalog reached via this connection?"
    )

    _check_name_w_replace = field_validator("name")(
        validators.name_alphanumeric_w_replace
    )

    @field_validator("system_type")
    @classmethod
    def available_system_type(cls, value):
        available_systems = [
            cls.azure_synapse_key,
            cls.sql_server_nativ_key,
            cls.azure_server_nativ_key,
            cls.snowflake_nativ_key,
            cls.azure_blob_key,
            cls.oracle_key,
            cls.db2_key,
            cls.postgresql_key,
            cls.azurepostgresql_key,
        ]
        if value not in available_systems:
            raise ValueError("is unknown system type")
        return value

    @property
    def is_snowflake_nativ(self) -> bool:
        return self.system_type == self.snowflake_nativ_key

    @property
    def is_azure_sql_nativ(self) -> bool:
        return self.system_type == self.azure_server_nativ_key

    @property
    def is_sql_server_nativ(self) -> bool:
        return self.system_type == self.sql_server_nativ_key

    @property
    def is_synapse_nativ(self) -> bool:
        return self.system_type == self.azure_synapse_key

    @property
    def is_db2_nativ(self) -> bool:
        return self.system_type == self.db2_key

    @property
    def is_postgres_sql_nativ(self) -> bool:
        return self.system_type == self.postgresql_key

    @property
    def is_azurepostgres_sql_nativ(self) -> bool:
        return self.system_type == self.azurepostgresql_key

    @property
    def is_oracle_db(self) -> bool:
        return self.system_type == self.oracle_key

    @property
    def is_azure_blob(self) -> bool:
        return self.system_type == self.azure_blob_key

    @property
    def is_tsql(self) -> bool:
        return (
            self.is_synapse_nativ or self.is_azure_sql_nativ or self.is_sql_server_nativ
        )

    def get_short_id(self) -> str:
        return str(self.id).split("-")[0]


class Connections(BaseModel):
    """Base class for loading CLOE Connection model objects."""

    subfolder_path: ClassVar[pathlib.Path] = pathlib.Path("jobs", "connections")

    connections: list[Connection] = []

    _connections_cache: dict[uuid.UUID, Connection] = {}

    @field_validator("connections")
    @classmethod
    def child_uniqueness_check(cls, value: list[Connection]):
        validators.find_non_unique(value, "name")
        return value

    @classmethod
    def read_instances_from_disk(
        cls, input_path: pathlib.Path
    ) -> tuple[Connections, list[ValidationError | json.JSONDecodeError]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        instances, errors = Connection.read_instances_from_disk(
            input_path / cls.subfolder_path
        )
        try:
            instance = cls(connections=instances)
        except ValidationError as e:
            errors.append(e)

        return instance, errors

    def write_to_disk(self, output_path: pathlib.Path) -> None:
        for child in self.connections:
            child.write_to_disk(output_path / self.subfolder_path)

    def get_connections(self) -> dict[uuid.UUID, Connection]:
        if len(self._connections_cache) < 1:
            self._connections_cache = {
                connection.id: connection for connection in self.connections
            }
        return self._connections_cache

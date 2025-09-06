import logging
import uuid

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from cloe_metadata import base
from cloe_metadata.shared import repository
from cloe_metadata.utils.templating_engine.general_templates import env

logger = logging.getLogger(__name__)


class DB2FS(BaseModel):
    """Class for advanced or shared DB2FS functionality."""

    base_obj: base.DB2FS
    dataset_types: base.DatasetTypes = Field(..., exclude=True)
    databases: base.Databases = Field(..., exclude=True)
    data_source_infos: dict[uuid.UUID, repository.DataSourceInfo] = Field(
        ..., exclude=True
    )
    connections: base.Connections

    @field_validator("dataset_types")
    @classmethod
    def dataset_type_exists(cls, value: base.DatasetTypes, info: ValidationInfo):
        """Validates that the dataset type exists."""
        base_obj: base.DB2FS | None = info.data.get("base_obj")
        if (
            base_obj is not None
            and base_obj.dataset_type_id not in value.get_dataset_types()
        ):
            raise ValueError("dataset_type_id does not exist")
        return value

    @field_validator("data_source_infos")
    @classmethod
    def data_source_infos_exists(
        cls, value: dict[uuid.UUID, repository.DataSourceInfo], info: ValidationInfo
    ):
        """Validates that the data source info exists."""
        base_obj: base.DB2FS | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.datasource_info_id not in value:
            raise ValueError("datasource_info_id not in datasource_infos")
        return value

    @field_validator("databases")
    @classmethod
    def tables_exists(cls, value: base.Databases, info: ValidationInfo):
        """Validates that the tables exist in the databases."""
        base_obj: base.DB2FS | None = info.data.get("base_obj")
        if base_obj is not None and base_obj.source_table_id not in value.id_to_tables:
            raise ValueError("id not in tables")
        return value

    @field_validator("connections")
    @classmethod
    def sink_connection_exists(cls, value: base.Connections, info: ValidationInfo):
        """Validates that the sink connection exists in the connections."""
        base_obj: base.DB2FS | None = info.data.get("base_obj")
        error_text = ""
        if (
            base_obj is not None
            and base_obj.sink_connection_id not in value.get_connections()
        ):
            error_text += "sink_connection_id "
        if (
            base_obj is not None
            and base_obj.source_connection_id not in value.get_connections()
        ):
            error_text += " source_connection_id "
        if len(error_text) > 1:
            raise ValueError(f"{error_text} not in connections")
        return value

    @property
    def source_connection(self) -> base.Connection:
        """Returns the source connection object."""
        return self.connections.get_connections()[self.base_obj.source_connection_id]

    @property
    def sink_connection(self) -> base.Connection:
        """Returns the sink connection object."""
        return self.connections.get_connections()[self.base_obj.sink_connection_id]

    @property
    def source_table(self) -> base.Table:
        """Returns the source table object."""
        return self.databases.id_to_tables[self.base_obj.source_table_id]

    @property
    def dataset_type(self) -> base.DatasetType:
        """Returns the dataset type object."""
        return self.dataset_types.get_dataset_types()[self.base_obj.dataset_type_id]

    @property
    def data_source_info(self) -> repository.DataSourceInfo:
        """Returns the data source info object."""
        return self.data_source_infos[self.base_obj.datasource_info_id]

    @property
    def rendered_folder_path(self) -> str:
        """
        Renders and returns the folder path using Jinja2 templates.

        The following variables can be used in the Jinja template:

        - `content`: The content of the data source info's base object.
        - `sourcesystem_name`: The name of the source system.
        - `tenant`: The name of the tenant (if available).
        - `object_description`: The description of the base object.
        - `ds_type_name`: The name of the dataset type.

        Example Jinja template:
        ```
        {% if tenant %}
            /{{ tenant }}/{{ sourcesystem_name }}/{{ ds_type_name }}/
        {% else %}
            /{{ sourcesystem_name }}/{{ ds_type_name }}/
        {% endif %}
        ```

        Returns:
            str: The rendered folder path.
        """
        if self.base_obj.folder_path is None:
            return self.data_source_info.sourcesystem.name
        tenant_name = None
        if self.data_source_info.tenant is not None:
            tenant_name = self.data_source_info.tenant.name
        return env.from_string(self.base_obj.folder_path).render(
            content=self.data_source_info.base_obj.content,
            sourcesystem_name=self.data_source_info.sourcesystem.name,
            tenant=tenant_name,
            object_description=self.data_source_info.base_obj.object_description,
            ds_type_name=self.dataset_type.name,
        )

    @property
    def rendered_select_query(self) -> str:
        """
        Renders and returns the select query using Jinja2 templates.

        The following variables can be used in the Jinja template:

        - `source_table_identifier`: The identifier for the source table.
        - `source_table`: The source table object.
        - `source_columns`: The columns of the source table.
        - `source_sourcesystem_name`: The name of the source system.
        - `source_datasettype_name`: The name of the dataset type.
        - `source_datasettype_type`: The storage format of the dataset type.
        - `sequence_column_name`: The name of the sequence column.

        Example Jinja template:
        ```
        SELECT {{ source_columns | join(', ') }}
        FROM {{ source_table_identifier }}
        WHERE {{ sequence_column_name }} > :last_sequence_value
        ```

        Returns:
            str: The rendered select query.
        """
        source_schema, source_table = self.databases.get_table_and_schema(
            self.base_obj.source_table_id
        )
        template = env.get_template("object_identifier.sql.j2")
        source_table_identifier = template.render(
            connection=self.source_connection,
            schema_obj=source_schema,
            table_obj=source_table,
        )
        datasource_infos_name = self.data_source_info.sourcesystem.name
        ds_type_name = self.dataset_types.get_dataset_types()[
            self.base_obj.dataset_type_id
        ].name
        ds_type_type = self.dataset_types.get_dataset_types()[
            self.base_obj.dataset_type_id
        ].storage_format
        return env.from_string(self.base_obj.select_statement).render(
            source_table_identifier=source_table_identifier,
            source_table=self.source_table,
            source_columns=self.source_table.columns,
            source_sourcesystem_name=datasource_infos_name,
            source_datasettype_name=ds_type_name,
            source_datasettype_type=ds_type_type,
            sequence_column_name=self.base_obj.sequence_column_name,
        )

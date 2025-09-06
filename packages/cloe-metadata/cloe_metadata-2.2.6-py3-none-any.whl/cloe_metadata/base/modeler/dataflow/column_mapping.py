import logging
import uuid

from pydantic import BaseModel, ConfigDict, Field

import cloe_metadata.utils.writer as writer

logger = logging.getLogger(__name__)


class ColumnMapping(BaseModel):
    """Dataflow ColumnMapping metadata model base class"""

    source_column_name: str | None = Field(
        default=None,
        description="Name of source column or column alias if calculation is used.",
    )
    is_insert: bool = Field(default=True, description="Should column be included when inserting?")
    is_update: bool = Field(default=True, description="Should column be included when updating?")
    is_load_on_convert_error: bool = Field(
        default=True,
        description="Should column be loaded when a DQ2 error occurs(ignored if DQ2 is off)?",
    )
    is_logging_on_convert_error: bool = Field(
        default=True,
        description="Should a logging entry be created if an DQ2 error occurs(ignored if DQ2 is off)?",
    )
    sink_table_id: uuid.UUID = Field(..., description="Reference to the sink table")
    convert_to_datatype: str | None = Field(default=None, description="Reference to a convert template")
    bk_order: int | None = Field(
        default=None,
        description="If set this column is used to generate the BK. Number indicates ordering within BK.",
    )
    sink_column_name: str | None = Field(
        default=None,
        description="Name of sink column. Can be empty if source column value only used for BK.",
    )
    calculation: str | None = Field(
        default=None,
        description="Free calculation, must contain complete artifact for "
        "SELECT including table alias! (e.g. SUM(**s.**sales))",
    )
    on_convert_error_value: str | None = Field(
        default=None,
        description="If IsLoadOnConvertError is set and a DQ2 error occurs this value is "
        "used instead of  the default value defined in the conversion template(ignored if DQ2 is off).",
    )
    on_null_value: str | None = Field(default=None, description="If source column value is NULL this value is used.")
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)

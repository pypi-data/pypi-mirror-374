import logging
import uuid

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

import cloe_metadata.utils.writer as writer
from cloe_metadata.utils import validators

logger = logging.getLogger(__name__)


class LookupParameter(BaseModel):
    """Dataflow LookupParameter metadata model base class"""

    source_column_name: str = Field(..., description="Name of source column to be used in lookup bk")
    calculation: str | None = Field(
        default=None,
        description="Free calculation, must contain complete artifact for "
        "SELECT including table alias! (e.g. SUM(**s.**sales))",
    )
    order_by: int = Field(..., description="Number indicates ordering within lookup BK.")
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)


class ReturnColumnMapping(BaseModel):
    """Dataflow ReturnColumnMapping metadata model base class"""

    sink_table_id: uuid.UUID = Field(..., description="Reference to the sink table")
    on_null_value: str = Field(..., description="If lookup column value is NULL this value is used.")
    return_column_name: str = Field(..., description="Name of lookuptable source column.")
    sink_column_name: str = Field(..., description="Name of sink column.")
    is_insert: bool = Field(default=True, description="Should column be included when inserting?")
    is_update: bool = Field(default=True, description="Should column be included when updating?")
    is_logging_on_lookup_error: bool = Field(
        default=False,
        description="Should a logging entry be created if an DQ3 error occurs(ignored if DQ3 is off)?",
    )
    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)


class Lookup(BaseModel):
    """Dataflow Lookup metadata model base class"""

    name: str = Field(..., description="Name of the lookup(must be unique)")
    lookup_parameters: list[LookupParameter]
    lookup_table_id: uuid.UUID = Field(..., description="Reference to the lookup table")
    is_add_tenant_to_lookup_parameter: bool = Field(
        default=False,
        description="Should table tenant be added to lookup BK parameters?",
    )
    sink_lookup_bk_column_name: str | None = Field(default=None, description="BK column name in sink table")
    lookup_column_name: str | None = Field(default=None, description="Lookup table BK column name")
    lookup_valid_parameter_column_name: str | None = Field(
        default=None, description="Lookup2 column of the source table"
    )
    lookup_valid_from_column_name: str | None = Field(
        default=None, description="Lookup2 BETWEEN from column of lookuptable"
    )
    lookup_valid_to_column_name: str | None = Field(
        default=None, description="Lookup2 BETWEEN to column of lookuptables"
    )
    return_column_mappings: list[ReturnColumnMapping]

    model_config = ConfigDict(populate_by_name=True, alias_generator=writer.to_lower_camel_case)

    _check_name_w_replace = field_validator("name")(validators.name_alphanumeric_w_replace)

    @field_validator("lookup_parameters")
    @classmethod
    def lookup_parameters_order_by_unique_check(cls, value: list[LookupParameter]):
        order_number = []
        for lp in value:
            if lp.order_by not in order_number:
                order_number.append(lp.order_by)
            else:
                raise ValueError("order_by not unique")
        return value

    @field_validator("lookup_column_name")
    @classmethod
    def lookup_parameters_if_column_name(cls, value, info: ValidationInfo):
        if len(info.data.get("lookup_parameters", [])) > 0:
            return value
        raise ValueError("lookup column name set but no lookup parameters defined.")

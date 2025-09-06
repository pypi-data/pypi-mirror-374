from pydantic import BaseModel, ConfigDict, Field

from cloe_metadata.utils import writer


class Column(BaseModel):
    """Base class for loading Column model objects."""

    comment: str | None = Field(default=None, description="Comment")
    constraints: str | None = Field(default=None, description="e.g. default value")
    data_type: str = Field(..., description="DataType of column")
    data_type_length: int | None = Field(
        default=None, description="For string datatypes"
    )
    data_type_numeric_scale: int | None = Field(
        default=None, description="For Numeric datatypes"
    )
    data_type_precision: int | None = Field(
        default=None, description="For Float datatypes"
    )
    is_key: bool | None = Field(default=None, description="Identity Column?")
    is_nullable: bool | None = Field(default=None, description="Nullable?")
    labels: str | None = Field(default=None, description="Label")
    name: str = Field(..., description="Name of the column")
    ordinal_position: int | None = Field(default=None)
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

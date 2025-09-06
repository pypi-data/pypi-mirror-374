import uuid

from pydantic import BaseModel, ConfigDict, Field

import cloe_metadata.utils.writer as writer


class SourceTable(BaseModel):
    """Dataflow SourceTable metadata model base class"""

    table_id: uuid.UUID = Field(..., description="Reference to the source table")
    order_by: int = Field(..., description="Processing order for tables")
    is_active: bool = Field(default=True, description="Should table be processed?")
    tenant_id: uuid.UUID | None = Field(default=None, description="Reference to tenant")
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

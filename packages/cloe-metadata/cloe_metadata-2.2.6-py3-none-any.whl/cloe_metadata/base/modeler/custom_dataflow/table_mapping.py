import logging
import uuid

from pydantic import BaseModel, ConfigDict, Field

import cloe_metadata.utils.writer as writer

logger = logging.getLogger(__name__)


class TableMapping(BaseModel):
    """CustomDataflow TableMapping metadata model base class"""

    source_table_id: uuid.UUID = Field(..., description="Reference the source table")
    sink_table_id: uuid.UUID = Field(..., description="Reference the sink table")
    order_by: int = Field(..., description="Load order of the table")

    model_config = ConfigDict(
        populate_by_name=True, alias_generator=writer.to_lower_camel_case
    )

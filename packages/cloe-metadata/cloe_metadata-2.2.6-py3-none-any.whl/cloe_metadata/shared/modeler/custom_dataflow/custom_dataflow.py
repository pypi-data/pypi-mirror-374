import logging

from pydantic import BaseModel

from cloe_metadata import base
from cloe_metadata.shared.modeler.custom_dataflow import table_mapping

logger = logging.getLogger(__name__)


class CustomDataflow(BaseModel):
    """Class for advanced or shared CustomDataflow functionality."""

    base_obj: base.CustomDataflow
    shared_table_mappings: list[table_mapping.TableMapping]

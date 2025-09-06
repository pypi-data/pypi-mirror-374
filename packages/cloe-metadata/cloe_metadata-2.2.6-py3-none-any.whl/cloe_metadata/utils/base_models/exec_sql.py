import logging

import cloe_metadata.utils.base as util_base
from cloe_metadata.base.jobs import exec_sql

logger = logging.getLogger(__name__)


def get_rendered_query(query: exec_sql.Query) -> str:
    return util_base.get_rendered_text(query.query)

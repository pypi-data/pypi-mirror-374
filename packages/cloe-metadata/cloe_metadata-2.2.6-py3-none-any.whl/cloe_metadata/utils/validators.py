import re
from collections import Counter
from collections.abc import Sequence
from typing import Any

from jinja2 import Template, TemplateSyntaxError
from pydantic import BaseModel, ValidationInfo

REGEX_ALPHANUMERIC_W = r"[^a-zA-ZäöüÄÖÜß0-9_ {}]"


def name_alphanumeric_w_replace(name: str) -> str:
    """Function checks for non alphanumeric character
    and removes whitespace
    """
    if re.search(REGEX_ALPHANUMERIC_W, name):
        raise ValueError("must be alphanumeric including '_', ' '")
    return name.replace(" ", "_")


def name_alphanumeric(name: str) -> str:
    """Function checks for non alphanumeric character."""
    if re.search(REGEX_ALPHANUMERIC_W, name):
        raise ValueError("must be alphanumeric including '_', ' '")
    return name


def name_alphanumeric_table_name(name: str, info: ValidationInfo) -> str:
    """Function checks for non alphanumeric character. Special
    function for table name checks also taking level into account
    """
    if info.data.get("level", "") in (
        "core",
        "lu",
        "ver",
    ) and re.search(REGEX_ALPHANUMERIC_W, name):
        raise ValueError("must be alphanumeric including '_'," " ' ' for all levels except src/stg/derived")
    return name


def name_alphanumeric_table_columns(column: Any, info: ValidationInfo) -> Any:
    """Function checks for non alphanumeric character. Special
    function for table column name checks also taking level into account
    """
    if info.data.get("level", "") in (
        "core",
        "lu",
        "ver",
    ) and re.search(REGEX_ALPHANUMERIC_W, column.name):
        raise ValueError("column name must be alphanumeric including '_'," " ' ' for all levels except src/stg/derived")
    return column


def find_non_unique(models: Sequence[BaseModel], attribute: str) -> list[BaseModel]:
    """
    Find non-unique values for a given attribute in a list of Pydantic models.

    :param models: List of Pydantic model instances.
    :param attribute: The attribute name to check for uniqueness.
    :return: List of non-unique values for the specified attribute.
    """
    # Extract the values of the specified attribute
    values = [getattr(model, attribute) for model in models]

    # Count occurrences
    value_counts = Counter(values)

    # Identify non-unique values
    non_unique = [value for value, count in value_counts.items() if count > 1]

    if len(non_unique) > 0:
        raise ValueError(f"do not have unique values for attribute '{attribute}'. These are duplicated {non_unique}")

    return non_unique


def check_if_valid_template(name: str) -> str:
    try:
        Template(name)
    except TemplateSyntaxError:
        raise ValueError("template is no valid jinja2 template") from None
    return name

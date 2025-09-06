import os
import re

from jinja2 import Environment, PackageLoader


def regex_replace(text: str, find: str, replace: str) -> str:
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, text)


def get_jinja_env(loader: PackageLoader | None = None) -> Environment:
    build_variables = {
        name: val for name, val in os.environ.items() if "CLOE_BUILD_" in name
    }
    template_env = Environment(loader=loader)
    template_env.globals |= build_variables

    template_env.filters["regex_replace"] = regex_replace
    return template_env

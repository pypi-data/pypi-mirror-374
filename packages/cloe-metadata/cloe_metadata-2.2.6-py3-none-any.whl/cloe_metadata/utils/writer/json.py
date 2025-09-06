import re


def to_lower_camel_case(name: str) -> str:
    name = "".join(word.capitalize() for word in name.split("_"))
    name = f"{name[:1].lower()}{name[1:]}"
    name = re.sub(r"Id$", "ID", name)
    return re.sub(r"Dq", "DQ", name)

from cloe_metadata.utils import templating_engine


def get_rendered_text(text: str) -> str:
    template = templating_engine.get_jinja_env().from_string(text)
    return template.render()

from typing import Optional, Any, Dict

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("bot", "templates"),
    autoescape=select_autoescape(["html"]),
)


def render_template(name: str, values: Optional[Dict[str, Any]] = None, **kwargs):
    template = env.get_template(name)
    if values:
        rendered_template = template.render(values, **kwargs)
    else:
        rendered_template = template.render(**kwargs)
    return rendered_template

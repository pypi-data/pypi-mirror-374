from jinja2 import PackageLoader

from .get_jinja_env import get_jinja_env

package_loader = PackageLoader("cloe_metadata.utils", "templates")
env = get_jinja_env(package_loader)

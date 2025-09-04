"""Top-level package for Simularium Models Util."""

__author__ = "Blair Lyons"
__email__ = "blairl@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.0"


def get_module_version():
    return __version__


from .common import (
    ReaddyUtil,  # noqa: F401
    RepeatedTimer,  # noqa: F401
)

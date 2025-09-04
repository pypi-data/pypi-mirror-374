"""jupyter_advanced_latex package."""

from .magics import (
    load_ipython_extension,
    unload_ipython_extension,
    register_ipython_extension,
)

__all__ = [
    "load_ipython_extension",
    "unload_ipython_extension",
    "register_ipython_extension",
]

__version__ = "0.1.0"


from . import magics

try:
    from IPython import get_ipython

    ip = get_ipython()
    if ip is not None:
        magics.load_ipython_extension(ip)
except ImportError:
    pass

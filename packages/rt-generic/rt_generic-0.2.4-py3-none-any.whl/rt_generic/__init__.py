#! /usr/bin/env python
from sys import version_info
from tomlkit import api as toml_api
from .utils import get_pyproject

# mypy trys to import even for versions < 3.8
if (3, 8) <= version_info:
    from importlib import metadata # type: ignore[attr-defined]

try:
    fn = get_pyproject()
    with open(fn, 'r') as fp :
        pyproject = toml_api.load(fp)
        if (isinstance(pyproject, dict)
            and 'project' in pyproject
            and isinstance(pyproject['project'], dict)
            and 'version' in pyproject['project']
            and isinstance(pyproject['project']['version'], str)
            ):
            __version__ : str = pyproject['project']['version']
        else:
            raise ValueError("could not find project.version in pyproject.toml")
except ValueError as e :
    try:
        if (3, 8) <= version_info:
            __version__ = metadata.version("rt_generic")
            
    except metadata.PackageNotFoundError:  # pragma: no cover
        pass
    finally:
        try :
            from .version import __version__
        except ModuleNotFoundError:
            __version__ = "uninstalled and no pyproject.toml"

if version_info < (3, 7):
    raise NameError(
        f"""
        This package uses type information not avaialbe in ({version_info}). It
        first becomes avaiable in version 3.7.
        """
    )

from . import type_setup
from .rt_generic import *

__all__ = [
    '__version__',
    'RTGeneric',
    'TrueT',
    'FalseT',
    'TypeErrorT',
    'has_any_TypeVar',
    ]

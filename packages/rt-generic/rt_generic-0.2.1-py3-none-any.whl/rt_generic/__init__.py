#! /usr/bin/env python

from sys import version_info

if version_info < (3, 7):
    raise NameError(
        f"""
        This package uses type information not avaialbe in ({version_info}). It
        first becomes avaiable in version 3.7.
        """
    )

from . import type_setup
from .rt_generic import *

all = [
    "TrueT",
    "FalseT",
    "TypeErrorT",
    "RTGeneric",
]

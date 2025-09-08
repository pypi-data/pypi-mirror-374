#! /usr/bin/env python
from __future__ import annotations

"""
Get a bunch of type imports regardless of python version (back to 3.7). Breaks
imports down by python minor version number, and uses code for missing imports.
The code is typically stolen from later version python libraries, slightly
adapted if necessary for earlier versions.
"""

import sys  # For version_info (so code can account for old python)

# avoid (3, M) <= sys.version_info < (3,N) ... mypy does not understand
# Instead, the upper bound is implicit in what has been checked before
if (3, 12) <= sys.version_info:
    from types import get_original_bases
    from typing import (
        TypeAlias,
        TypeVar,
        ClassVar,
        Generic,
        Any,
        Self,
        assert_type,
        Literal,
        get_args,
        get_origin,
    )
elif (3, 11) <= sys.version_info:
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(f"Expected an instance of type, not {type(cls).__name__!r}") from None

    from typing import (
        TypeAlias,
        TypeVar,
        ClassVar,
        Generic,
        Any,
        Self,
        assert_type,
        Literal,
        get_args,
        get_origin,
    )
elif (3, 10) <= sys.version_info:
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(f"Expected an instance of type, not {type(cls).__name__!r}") from None

    from typing_extensions import Self, assert_type

    from typing import (
        TypeVar,
        ClassVar,
        Generic,
        Any,
        Literal,
        get_args,
        get_origin,
    )

    from types import GenericAlias
elif (3, 9) <= sys.version_info:
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(f"Expected an instance of type, not {type(cls).__name__!r}") from None

    from typing_extensions import TypeAlias, Self, assert_type

    from typing import (
        TypeVar,
        ClassVar,
        Generic,
        Any,
        Literal,
        get_args,
        get_origin,
    )

    from types import GenericAlias
elif (3, 8) <= sys.version_info:
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(f"Expected an instance of type, not {type(cls).__name__!r}") from None

    from typing_extensions import TypeAlias, Self, assert_type

    from typing import (
        TypeVar,
        ClassVar,
        Generic,
        Any,
        Literal,
        get_args,
        get_origin,
    )
    from typing import List as __List

    GenericAlias: type = type(__List[int])
elif (3, 7) <= sys.version_info:
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(f"Expected an instance of type, not {type(cls).__name__!r}") from None

    # redef actually handled by big if/elif/elif/else,
    # and mypy doesn't like python's def of Literal
    from typing_extensions import (
        TypeAlias,
        Self,
        assert_type,
        Literal,
        get_args,
        get_origin,
    )
    from typing import TypeVar, ClassVar, Generic, Any
    from typing import List as __List

    # redef actually handled by big if/elif/elif/else,
    GenericAlias: type = type(__List[int])
else:
    raise Exception("rt_generic requires python version >= 3.7")

from typing import Tuple, Dict, List, TYPE_CHECKING, Union

LiteralGenericAlias: type = type(Literal[True])
NoneType: type = type(None)

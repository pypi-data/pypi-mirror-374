#! /usr/bin/env python
from __future__ import annotations

"""
Get a bunch of type imports regardless of python version (back to 3.7)
"""

import sys  # For version_info (so code can account for old python)

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
elif (3, 11) <= sys.version_info < (3, 12):
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(
                f"Expected an instance of type, not {type(cls).__name__!r}"
            ) from None

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
elif (3, 10) <= sys.version_info < (3, 11):
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(
                f"Expected an instance of type, not {type(cls).__name__!r}"
            ) from None

    from typing_extensions import Self, assert_type
    from typing import TypeVar, ClassVar, Generic, Any, Literal, get_args, get_origin
    from types import GenericAlias
elif (3, 9) <= sys.version_info < (3, 10):
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(
                f"Expected an instance of type, not {type(cls).__name__!r}"
            ) from None

    from typing_extensions import TypeAlias, Self, assert_type
    from typing import TypeVar, ClassVar, Generic, Any, Literal, get_args, get_origin
    from types import GenericAlias
elif (3, 8) <= sys.version_info < (3, 9):
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(
                f"Expected an instance of type, not {type(cls).__name__!r}"
            ) from None

    from typing_extensions import TypeAlias, Self, assert_type
    from typing import TypeVar, ClassVar, Generic, Any, Literal, get_args, get_origin
    from typing import List as __List

    GenericAlias: type = type(__List[int])
elif (3, 7) <= sys.version_info < (3, 8):
    # Stolen code from 3.13
    def get_original_bases(cls):
        try:
            return cls.__dict__.get("__orig_bases__", cls.__bases__)
        except AttributeError:
            raise TypeError(
                f"Expected an instance of type, not {type(cls).__name__!r}"
            ) from None

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

    GenericAlias: type = type(__List[int])
else:
    raise Exception("typingkit requires python version >= 3.7")

from typing import Tuple, Dict, List, TYPE_CHECKING, Union

LiteralGenericAlias: type = type(Literal[True])

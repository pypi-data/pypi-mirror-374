#!/usr/bin/env python
from __future__ import annotations
from sys import version_info

# all type constraints turned into strings, and not parsed
import unittest

# import rt_generic
from rt_generic import RTGeneric, TrueT, FalseT, TypeErrorT
from rt_generic.type_setup import *

# Define classes and typevars external to test class, as I was having
# difficulty getting the names right
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class E_Cls1(RTGeneric, Generic[T, U, V]):
    def __init__(self, t: T, u: U, v: V):
        super().__init__()
        self.t: T = t
        self.u: U = u
        self.v: V = v
        return

    # mypy is ignoring this check for old versions, and not needing exemption for new
    if (3, 10) <= version_info:

        def fn0(self) -> tuple[str, type, type, type]:  # type: ignore[misc,unused-ignore]
            return ("", type(None), type(None), type(None))

    else:

        def fn0(self) -> Tuple[str, type, type, type]:
            return ("", type(None), type(None), type(None))

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # print(f"init subclass {cls} of E_Cls1")
        # mypy can't imagine any use for passing in a TypeVar
        utype = cls.tv2type(E_Cls1, U)  # type: ignore[misc]
        if utype == TypeErrorT:
            # print(f"\tdefering until we have a subclass without remaining generics")
            return
        if cls.generic_true(E_Cls1, U): # type: ignore[misc]

            def _fn0(self):
                # mypy can't imagine any use for passing in a TypeVar
                ttype = self.tv2type(E_Cls1, T)  # type: ignore[misc]
                utype = self.tv2type(E_Cls1, U)  # type: ignore[misc]
                vtype = self.tv2type(E_Cls1, V)  # type: ignore[misc]
                return ("modified", ttype, utype, vtype)

        else:

            def _fn0(self):
                # mypy can't imagine any use for passing in a TypeVar
                ttype = self.tv2type(E_Cls1, T)  # type: ignore[misc]
                utype = self.tv2type(E_Cls1, U)  # type: ignore[misc]
                vtype = self.tv2type(E_Cls1, V)  # type: ignore[misc]
                return ("normal", ttype, utype, vtype)

        cls.fn0 = _fn0  # type: ignore[method-assign]

    def fn1(self):
        # mypy can't imagine any use for passing in a TypeVar
        ttype = self.tv2type(E_Cls1, T)  # type: ignore[misc]
        utype = self.tv2type(E_Cls1, U)  # type: ignore[misc]
        vtype = self.tv2type(E_Cls1, V)  # type: ignore[misc]
        return (ttype, utype, vtype)


if (3, 10) > version_info:

    class E_Cls2(
        E_Cls1[int, TrueT, Tuple[Tuple[T, ...], List[Dict[str, T]]]],
        RTGeneric,
    ):
        def __init__(self):
            # print(f"initialize E_Cls2")
            return

        # I need because I have my own RTGeneric, and I want to know MY mapping
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            # print(f"init subclass {cls} of E_Cls2")
            return

        def fn2(self):
            # mypy can't imagine any use for passing in a TypeVar
            ttype = self.tv2type(E_Cls2, T)  # type: ignore[misc]
            return (ttype,)

else:
    # mypy is not handling if/else on version here
    class E_Cls2(  # type: ignore[no-redef]
        E_Cls1[int, TrueT, tuple[tuple[T, ...], list[dict[str, T]]]],  # type: ignore[misc,unused-ignore]
        RTGeneric,
    ):
        def __init__(self):
            # print(f"initialize E_Cls2")
            return

        # I need because I have my own RTGeneric, and I want to know MY mapping
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            # print(f"init subclass {cls} of E_Cls2")
            return

        def fn2(self):
            # mypy can't imagine any use for passing in a TypeVar
            ttype = self.tv2type(E_Cls2, T)  # type: ignore[misc]
            return (ttype,)


class E_Cls3(E_Cls1[str, FalseT, float]):
    def __init__(self):
        return


class E_Cls4(E_Cls1[Literal[1, 2, 3], TrueT, float]):
    def __init__(self):
        return


class E_Cls5(E_Cls2[float]):
    def __init__(self):
        return


class T_Cls(unittest.TestCase):
    # Python does not permit duplicate base classes
    # TypeError: duplicate base class E_Cls2
    # class E_Cls6(E_Cls2[int], E_Cls2[str]) :
    #     def __init__(self) :
    #         print(f"initialize E_Cls6")
    #         return
    #     pass

    # Python fails because "cannot create a consistent MRO"
    # TypeError: Cannot create a consistent method resolution order (MRO) for bases E_Cls1, E_Cls2
    # class E_Cls6(E_Cls1[int,str,float], E_Cls2[str]) :
    #     def __init__(self) :
    #         print(f"initialize E_Cls6")
    #         return
    #     pass

    def test_10_background_RT(self):
        self.assertEqual(type(T), TypeVar)
        self.assertEqual(type(U), TypeVar)
        self.assertEqual(type(V), TypeVar)

        c1 = E_Cls1[int, int, str](1, 2, "abc")
        self.assertEqual(type(c1), E_Cls1)

        self.assertEqual(type(TrueT), LiteralGenericAlias)
        self.assertEqual(c1.generic_lit_values(Literal[5, "abc"]), (5, "abc"))

    def test_11_Base_Class(self):
        c1 = E_Cls1(None, None, None)
        self.assertEqual(c1.fn0(), ("", NoneType, NoneType, NoneType))
        self.assertEqual(
            c1.fn1(),
            (
                TypeErrorT,
                TypeErrorT,
                TypeErrorT,
            ),
        )
        with self.assertRaises(AttributeError) as context:
            c1.fn2()  # type: ignore[attr-defined]
        self.assertEqual("'E_Cls1' object has no attribute 'fn2'", str(context.exception))

    def test_12_E_Cls3(self):
        c3 = E_Cls3()
        self.assertEqual(c3.fn0(), ("normal", str, FalseT, float))
        self.assertEqual(
            c3.fn1(),
            (
                str,
                FalseT,
                float,
            ),
        )
        with self.assertRaises(AttributeError) as context:
            c3.fn2()  # type: ignore[attr-defined]
        self.assertEqual("'E_Cls3' object has no attribute 'fn2'", str(context.exception))

    def test_13_E_Cls4(self):
        c4 = E_Cls4()
        self.assertEqual(c4.fn0(), ("modified", Literal[1, 2, 3], TrueT, float))
        self.assertEqual(
            c4.fn1(),
            (
                Literal[1, 2, 3],
                TrueT,
                float,
            ),
        )
        with self.assertRaises(AttributeError) as context:
            c4.fn2()  # type: ignore[attr-defined]
        self.assertEqual("'E_Cls4' object has no attribute 'fn2'", str(context.exception))

    def test_14_E_Cls5(self):
        c5 = E_Cls5()
        if (3, 10) > version_info:
            self.assertEqual(
                c5.fn0(),
                (
                    "modified",
                    int,
                    TrueT,
                    Tuple[Tuple[float, ...], List[Dict[str, float]]],
                ),
            )
            self.assertEqual(
                c5.fn1(),
                (int, TrueT, Tuple[Tuple[float, ...], List[Dict[str, float]]]),
            )
        else:
            self.assertEqual(
                c5.fn0(),
                (
                    "modified",
                    int,
                    TrueT,
                    # mypy is not handling if/else on version here (only old versions)
                    tuple[tuple[float, ...], list[dict[str, float]]],  # type: ignore[misc,unused-ignore]
                ),
            )
            self.assertEqual(
                c5.fn1(),
                # mypy is not handling if/else on version here (only old versions)
                (int, TrueT, tuple[tuple[float, ...], list[dict[str, float]]])  # type: ignore[misc,unused-ignore]
            )
        c5.fn2()


if __name__ == "__main__":
    unittest.main()

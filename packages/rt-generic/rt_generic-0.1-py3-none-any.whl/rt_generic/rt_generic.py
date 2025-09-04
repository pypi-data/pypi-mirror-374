from __future__ import (
    annotations,
)  # turn all anotations into strings, so the parser ignores them

# Get a bunch of type imports regardless of python version (back to 3.7)
from .type_setup import *

TrueT = Literal[True]
FalseT = Literal[False]
TypeErrorT = Literal["TypeError"]


def _get_original_bases(cls):
    """
    Like get_original_bases, but in error case return empty tuple
    """
    try:
        return get_original_bases(cls)
    except TypeError as e:
        return tuple()


class TypeVarIndex:
    def __init__(self, t: type, tv: TypeVar):
        self.value = (
            t.__module__,
            t,
            tv,
        )
        return

    @property
    def _module(self):
        return self.value[0]

    @property
    def _type(self):
        return self.value[1]

    @property
    def _typevar(self):
        return self.value[2]

    def __repr__(self):
        return f"({self._module},{self._type.__name__},{self._typevar.__name__})"

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeVarIndex):
            return NotImplemented
        return (
            self._module == other._module
            and self._type == other._type
            and self._typevar == other._typevar
        )


class TypeVarDict(Dict[TypeVarIndex, Union[type, TypeVar]]):
    def __init__(self):
        super().__init__()


def has_any_TypeVar(t: type) -> bool:
    if type(t) == TypeVar:
        return True
    for arg in get_args(t):
        if has_any_TypeVar(arg):
            return True
        else:
            pass  # continue looking
    if "__parameters__" in t.__dict__:
        for parameter in t.__dict__["__parameters__"]:
            if has_any_TypeVar(parameter):
                return True
            else:
                pass  # continue looking
    else:
        pass
    return False


def has_TypeVar(t: Union[type, TypeVar], tv: TypeVar) -> bool:
    if type(t) == TypeVar and t == tv:
        return True
    for arg in get_args(t):
        if has_TypeVar(arg, tv):
            return True
        else:
            pass  # continue looking
    return False


def fix_TypeVar(
    t: Union[type, TypeVar],
    t_orig: TypeVar,
    t_new: Union[type, TypeVar],
    depth: int = 0,
) -> Union[type, TypeVar]:
    tabs = "\t" * depth
    # print(f'{tabs}| fix_TypeVar({t} ({type(t)}, {get_origin(t)}, {get_args(t)})')
    result: Union[type, TypeVar] = t
    if not has_TypeVar(t, t_orig):
        pass  # nothing to do, result already == t
    elif type(t) == TypeVar:
        if t == t_orig:
            # print(f'{tabs}| switch to t_new({t_new})')
            result = t_new
        else:
            pass  # leave unchanged
    else:
        # print(f'{tabs}| fix arg list:')
        arglist: list[str] = []
        for arg in get_args(t):
            new_arg = fix_TypeVar(arg, t_orig, t_new, depth + 1)
            if str(new_arg)[0:1] != "<":
                arglist.append(str(new_arg))
            else:
                arglist.append(new_arg.__name__)
        # print(f'{tabs}|\t {arglist}')
        # I need to return t.__name__[arg1, arg2, ...]
        # but currently there seems no way to say that
        # so I build a string and use eval
        try:
            tname = t.__name__
        except AttributeError as e:
            tname = t._name  # type: ignore[attr-defined]
        if len(arglist) == 1:
            type_str = f"{tname}[{arglist[0]}]"
            # print(f'{tabs}| eval({type_str})')
            result = eval(type_str)
        elif len(arglist) > 1:
            type_str = f"{tname}[{arglist[0]}, "
            for arg in arglist[1:-1]:
                type_str += f"{arg}, "
            type_str += f"{arglist[-1]}]"
            # print(f'{tabs}| eval({type_str})')
            result = eval(type_str)
        else:
            result = t
    # print(f'{tabs}| return {result}')
    return result


# return should be Dict[tuple(cls,TypeVar), type|TypeVar]
# RTGeneric should copy this dict into cls_fix
# Then we offer a function tv2type(self, bcls, typevar) -> type
# that looks up (bcls, typevar)
import typing  # because when we we construct stuff, some base classes used to refer back to this


def fixup_generics(cls_fix: type) -> TypeVarDict:
    """
    creates a dict that maps (base_class, generic var in that class) -> actual type
    """
    result = TypeVarDict()
    bases = _get_original_bases(cls_fix)
    if len(bases) == 0:
        # print(f"No orig bases, so we can't compute dictionary")
        return TypeVarDict()
    for ob in bases:
        types = get_args(ob)
        base = get_origin(ob)
        if base == None or "__parameters__" not in base.__dict__:
            continue
        type_vars = base.__parameters__
        for tv, t in zip(type_vars, types):
            result[TypeVarIndex(base, tv)] = t
        if has_any_TypeVar(base):
            result2 = fixup_generics(base)
            new_result = TypeVarDict()
            for k2, t2 in result2.items():
                for k, t in result.items():
                    t2 = fix_TypeVar(t2, k._typevar, t)
                    new_result[k2] = t2
            for k, t in new_result.items():
                result[k] = t
        else:
            pass  # no more fixes wrt this base
    return result


class RTGeneric:
    """
    Base class which will add a dictionary to subclasses with information
    about actual types for the generic types the subclasses ancestors were
    defined with, as well as access functions for that dictionary.
    """

    _typevar_dict_ = TypeVarDict()

    def __init_subclass__(cls, **kwargs):
        """
        Configure any subclasses
        """
        if len(kwargs) != 0:
            print(
                f"RTGeneric __init_subclass__ is ignoring **kwargs ({kwargs}) because it only inherits from object, which does not accept them",
                file=sys.stderr,
            )
        super().__init_subclass__()
        # print(f"init subclass {cls} of RTGeneric")
        if not has_any_TypeVar(cls):
            d = fixup_generics(cls)
            if len(d) > 0:
                # print(f"Added _typevar_dict_ = {d}")
                cls._typevar_dict_ = d
            else:
                pass  # there were no fixups
        else:
            pass  # still has generic types, leave till subclass without
        return

    @classmethod
    def tv2type(cls, cls2: type, tv: TypeVar) -> Union(type, LiteralGenericAlias):  # type: ignore[valid-type]
        """
        if cls2 is a parent of cls, and cls2 used tv as a generic type
        then return the actual type tv respresents. This permits code
        in cls2 to decide on the correct action for the actual type.

        Checks in a dictionary which (should have been created) when cls
        was declared; cls should not have any remaining unassigned generic
        types.
        """
        if len(cls._typevar_dict_) > 0:
            if TypeVarIndex(cls2, tv) in cls._typevar_dict_:
                return cls._typevar_dict_[TypeVarIndex(cls2, tv)]
            else:
                # print(
                #    f"TypeErrorT due to no {TypeVarIndex(cls2, tv)} entry in {cls}._typevar_dict_\n{cls._typevar_dict_}"
                # )
                return TypeErrorT
        else:
            # print("TypeErrorT due to empty _typevar_dict_")
            return TypeErrorT
        return  # never gets here

    def inst_tv2type(self, cls2: type, tv: TypeVar) -> Union(type, LiteralGenericAlias):  # type: ignore[valid-type]
        """
        if class is a parent class, return the actual type of tv
        in class.
        (The above function, for the specific case where cls is
        the class this particular instance belongs to)
        """
        return self.__class__.tv2type(cls2, tv)

    @classmethod
    def generic_lit_values(cls, l: LiteralGenericAlias) -> tuple:  # type: ignore[valid-type]
        """
        if l is a Literal type, return a tuple of all the
        literals that can be in that type
        """
        if l != None and "__args__" in l.__dict__:  # type: ignore[attr-defined]
            # print(f"literal values of {l} are {l.__args__}")
            return l.__args__  # type: ignore[attr-defined]
        else:
            # print(f"no literal values of {l}")
            return ()

    @classmethod
    def generic_false(cls, l: LiteralGenericAlias) -> bool:  # type: ignore[valid-type]
        """
        if l is a literal type, return true if all the values (though
        usually "all" will be a single value") are in the set
        False, 'False', 'F', 'f', 'No', 'N', 'no', 'n', 0, None
        """
        values = cls.generic_lit_values(l)
        # print(f"checking falsness of {l} (values {values})")
        if len(values) == 0:
            return False
        result = False
        for v in values:
            result |= v in set(
                [False, "False", "F", "false", "f", "No", "N", "no", "n", 0, None]
            )
        return result

    @classmethod
    def generic_true(cls, l: LiteralGenericAlias) -> bool:  # type: ignore[valid-type]
        """
        if l is a literal type, return true if all the values (though
        usually "all" will be a single value") are in the set
        True, 'True', 'T', 'true', 't', 'Yes', 'Y', 'yes', 'y', 1
        """
        values = cls.generic_lit_values(l)
        if len(values) == 0:
            return False
        result = True
        for v in values:
            result &= v in set(
                [True, "true", "t", "True", "T", "yes", "y", "Yes", "Y", 1]
            )
        return result

RT-Generic

RT-Generic is a typed python module to make accessing the actual runtime types from a generic module more straight forward. It defines a base class RTGeneric which initializes each subclass (at subclass definition) with a mapping from (Class, TypeVar) to the actual type eventually assigned to that TypeVar. This permits me, for example, when creating `class GenClass[T,U,V](RTGeneric):` to write code which will behave appropriately for when I eventually create `class SubClass1(GenClass[int, float, dict[int, float]]):` and `class SubClass2(GenClass[tuple[str], list[float], dict[tuple[str], list[float]]]):`. [Repository](https://codeberg.org/Pusher2531/rt-generic.git), [PyPI](https://pypi.org/project/rt-generic/).

The process has 4 steps minimum (with a few optional steps along the way):  

1. Import RTGeneric from rt_generic. Importing * also brings three Literal types which can be useful.  
   * all brings in  
	 * class RTGeneric with class methods tv2type (converts TypeVar to actual type), generic_true (tests if Literal type means "True" or "Yes"), generic_false (tests if Literal type means "No" or "False"), and generic_lit_values (which gives a tuple of all literal values a Literal type represents).  
	 * TrueT, a Literal type for True.  
	 * FalseT, a Literal type for False.  
	 * TypeErrorT, a Literal type RTGeneric functions return when an error occured  
	 * function has_anyTypeVar(cls) -> bool, which can be used to check if all types in a class have been defined  
2. (Optionally) from rt_generic.type_setup import * for consistent types across python versions  
   * For all python versions supported by rt_generic, ensures that these are defined:  
	 * TypeAlias, GenericAlias, LiteralGenericAlias  
	 * TypeVar, ClassVar, Generic, Any, Literal, NoneType  
	 * Self  
	 * Union, Tuple, Dict, List, TYPE_CHECKING  
	 * get_args, get_origin, get_original_bases  
3. Declare your generic base class, based on Generic and RTGeneric
   * Either `class MyClass[T,U,V](RTGeneric):`, (python 3.11 or higher) or
   ```py
   T = TypeVar('T')
   U = TypeVar('U')
   V = TypeVar('V')
   class MyClass(RTGeneric, Generic[T,U,V]) :
   ```
4. Add self.tv2type (or cls.tv2type) calls in your base class where you need behavior to depend on actual types.  
   * Just to be clear, self.tv2type(MyClass,T) from an instance method, and cls.tv2type(MyClass,T) from a class method.  
   * You must specify your base class name for the `cls2` argument to tv2type, since you want to resolve TypeVars specified here. For example, using self.__class__ will attempt to resolve them according to the subclass, where there are no remaining TypeVars.  
   * This returns a **type**, so for example you might have `self.tv2type(MyClass, U) == List[int]`, but not `self.tv2type(MyClass, U) == [1,2]`.  
   * You can use Literal types to pass in values when you speciallize your class  
	 * To turn behavior on and off, use actual types `TrueT` or `FalseT`, and check in your code with `self.generic_true(MyClass, U)`  
	 * To set values to be used when you speciallize, for example, try using the actual type `Literal["Hello World"]`, and in your code `print(f"Custom Message: {self.generic_lit_values(self.tv2type(MyClass,V))[0]}")` (note index to select an element from the tuple returned by `generic_lit_values`).  
5. (Optionally) add a  
   ```py
	   def __init_subclass__(cls, **kwargs) :
		   super().__init_subclass(kwargs)
		   if not has_anyTypeVars(cls) :
		   ... # do your own setup, for example instantiate class
		   ... # variables of types represented by typevars,
		   ... # now that you know what those types are
   ```
5. (Optionally) declare subclasses which partially assign types to generics  
   * For example, `class MyClass2[T](MyClass[list[T], dict[str,T], Literal["mode2"]]):`. Note that in this case `tv2type(MyClass2,T) != tv2type(MyClass,T)`.  
5. Declare subclasses which fully assign types (possibly subclasses of other subclasses).  
   * This is required because RTGeneric works by initializing subclasses, and an anonymous subclass (as in `a = MyClass[int,int,dict[str, float]]()`) does not get initalized.  
   * instead do  
   ```py
	class MyFinalClass(MyClass[int,int,dict[str, float]]) :
		pass
	# or
	class MyFinalClass(MyClass2[str]]) :
		pass

	a = MyFinalClass()
   ```


RT-Generic

RT-Generic is a typed python module to make accessing the actual runtime types
from a generic module more straight forward. The process is as follows:

* Declare your generic class (shown "old style and new style"), adding RTGeneric as a base class
```py
# import stuff you need from types, typing, and/or typing_extensions

from rt_generic import * # deliberately not much
T = TypeVar('T')
U = TypeVar('U')
class MyClass(Generic[T,U], RTGeneric):
```
or
```py
# import stuff you need from types, typing, and/or typing_extensions

from rt_generic import * # deliberately not much
class MyClass[T,U](RTGeneric):
```
* In the body of your class, if you need to behave differently based on the type of one of the generic types, you can access it's type in a class method
```py
	@classmethod
	def cls_method(cls, argv) :
		T_type = cls.tv2type(MyClass,T) # type: ignore[misc] # mypy doesn't want T here
		if cls.generic_true(MyClass,U) # type: ignore[misc] # Was U set to TrueT (Literal type defined in rt-generic)
		...
```
 or an instance method:
```py
	def method(self, argv) :
		T_type = self.tv2type(MyClass,T) # type: ignore[misc] # mypy doesn't want T here
		if self.generic_true(MyClass,U) # type: ignore[misc] # Was U set to TrueT (Literal type defined in rt-generic)
		...
```
* Finally, RTGeneric relies on there being an explicit declartion of the non-generic particlar class(es)
```py
class B_Class(MyClass[float,FalseT]):
	pass
	
class C_Class(MyClass[list[int],TrueT]):
	pass
```

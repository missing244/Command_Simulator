__version__ = (1, 0, 0)

import ctypes,math
from typing import Union
my_super = super

class Numbur_Meta(type) :
    
    def __init__(self, *arg, **karg) :
        super().__init__(*arg, **karg)
        self._memory = {}
    
    def __call__(self, v:Union[int, float]) :
        if len(self._memory) > 131072 :
            for delkey in self._memory.keys() : break
            del self._memory[delkey]
        if v not in self._memory : self._memory[v] = super().__call__(v)
        return self._memory[v]

class _Number(metaclass=Numbur_Meta) :

    __slots__ = ["value"]
    
    def __setattr__(self, name, value):
        if name == "value" and not hasattr(self, "value") : super().__setattr__(name, value)
        elif name == "value"  : raise RuntimeError("value属性无法被重新赋值")

    def __hash__(self) :
        return self.value.__hash__()

    def __bool__(self) :
        return bool(self.value)


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __floordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __truediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __pow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))


    def __radd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other + self.value)
        else : return self.__class__(other.value + self.value)

    def __rsub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other - self.value)
        else : return self.__class__(other.value - self.value)

    def __rmul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other * self.value)
        else : return self.__class__(other.value * self.value)

    def __rfloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other // self.value)
        else : return self.__class__(other.value // self.value)

    def __rtruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other / self.value)
        else : return self.__class__(other.value / self.value)

    def __rpow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(other, self.value))
        else : return self.__class__(pow(other.value, self.value))


    def __iadd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __isub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __imul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __ifloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __itruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __ipow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))


    def __lt__(self, other) :
        if isinstance(other,(int,float)) : return self.value < other
        else : return self.value < other.value

    def __le__(self, other) :
        if isinstance(other,(int,float)) : return self.value <= other
        else : return self.value <= other.value

    def __eq__(self, other) :
        if isinstance(other,(int,float)) : return self.value == other
        elif isinstance(other,TYPE_TUPLE) : return self.value == other.value
        else : return False

    def __ne__(self, other) :
        if isinstance(other,(int,float)) : return self.value != other
        elif isinstance(other,TYPE_TUPLE) : return self.value != other.value
        else : return False

    def __gt__(self, other) :
        if isinstance(other,(int,float)) : return self.value > other
        else : return self.value > other.value

    def __ge__(self, other) :
        if isinstance(other,(int,float)) : return self.value >= other
        else : return self.value >= other.value


    def __neg__(self) :
        return self.__class__(-self.value)

    def __pos__(self) :
        return self.__class__(+self.value)

    def __abs__(self) :
        return self.__class__(abs(self.value))


    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return int(self.value)
    
    def __float__(self) :
        return float(self.value)


    def __round__(self, ndigits) :
        return round(self.value, ndigits)
    
    def __trunc__(self) :
        return math.trunc(self.value)

    def __floor__(self) :
        return math.floor(self.value)

    def __ceil__(self) :
        return math.ceil(self.value)


    def __str__(self) :
        return str(self.value)
    
    def __repr__(self) :
        return str(self.value)

class _Int(_Number) :

    __slots__ = ["value"]

    
    def __mod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __divmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)
    
    def __rmod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other % self.value)
        else : return self.__class__(other.value % self.value)

    def __rdivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(other, self.value)
        else : return divmod(other.value, self.value)

    def __imod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __idivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)


    def __lshift__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value >> other)
        else : return self.__class__(self.value >> other.value)

    def __rshift__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value << other)
        else : return self.__class__(self.value << other.value)

    def __and__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value & other)
        else : return self.__class__(self.value & other.value)

    def __xor__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value ^ other)
        else : return self.__class__(self.value ^ other.value)

    def __or__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value | other)
        else : return self.__class__(self.value | other.value)


    def __rlshift__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other >> self.value)
        else : return self.__class__(other.value >> self.value)

    def __rshift__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other << self.value)
        else : return self.__class__(other.value << self.value)

    def __rand__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other & self.value)
        else : return self.__class__(other.value & self.value)

    def __rxor__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other ^ self.value)
        else : return self.__class__(other.value ^ self.value)

    def __ror__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other | self.value)
        else : return self.__class__(other.value | self.value)


    def __ilshift__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value >> other)
        else : return self.__class__(self.value >> other.value)

    def __ishift__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value << other)
        else : return self.__class__(self.value << other.value)

    def __iand__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value & other)
        else : return self.__class__(self.value & other.value)

    def __ixor__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value ^ other)
        else : return self.__class__(self.value ^ other.value)

    def __ior__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value | other)
        else : return self.__class__(self.value | other.value)


    def __invert__(self) :
        return self.__class__(~self.value)

    def __index__(self) :
        return self.value


class float32(_Number) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        self.value = ctypes.c_float(float(value)).value

class float64(_Number) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        self.value = ctypes.c_double(float(value)).value

class int8(_Int) :

    def __init__(self, value: Union[str,int,float] = ...) -> None :
        self.value = ctypes.c_byte(float(value).__trunc__()).value

class int16(_Int) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        self.value = ctypes.c_int16(int(value)).value

class int32(_Int) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        self.value = ctypes.c_int32(int(value)).value

class int64(_Int) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        self.value = ctypes.c_int64(int(value)).value


TYPE_TUPLE = (float32, float64, int8, int16, int32, int64)
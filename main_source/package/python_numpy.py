import ctypes,math
from typing import Union

my_super = super

class float32(ctypes.c_float) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        my_super(float32,self).__init__(float(value))


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

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
        if isinstance(other,(int,float,type(None))) : return self.value == other
        else : return self.value == other.value

    def __ne__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value != other
        else : return self.value != other.value

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
    
    def __invert__(self) :
        return self.__class__(~self.value)
        

    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return int(self.value)
    
    def __float__(self) :
        return float(self.value)


    def __index__(self) :
        return self.value

    def __round__(self, ndigits) :
        return round(self.value,ndigits)
    
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


    def __hash__(self) :
        return self.value.__hash__()
    

class float64(ctypes.c_double) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        my_super(float64,self).__init__(float(value))


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

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
        if isinstance(other,(int,float,type(None))) : return self.value == other
        else : return self.value == other.value

    def __ne__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value != other
        else : return self.value != other.value

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
    
    def __invert__(self) :
        return self.__class__(~self.value)
        

    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return int(self.value)
    
    def __float__(self) :
        return float(self.value)


    def __index__(self) :
        return self.value

    def __round__(self, ndigits) :
        return round(self.value,ndigits)
    
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
    

    def __hash__(self) :
        return self.value.__hash__()


class int8(ctypes.c_int8) :

    def __init__(self, value: Union[str,int,float] = ...) -> None :
        my_super(int8,self).__init__(int(value))


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __truediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __floordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __mod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __divmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __pow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __radd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other + self.value)
        else : return self.__class__(other.value + self.value)

    def __rsub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other - self.value)
        else : return self.__class__(other.value - self.value)

    def __rmul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other * self.value)
        else : return self.__class__(other.value * self.value)

    def __rtruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other / self.value)
        else : return self.__class__(other.value / self.value)

    def __rfloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other // self.value)
        else : return self.__class__(other.value // self.value)

    def __rmod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other % self.value)
        else : return self.__class__(other.value % self.value)

    def __rdivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(other, self.value)
        else : return divmod(other.value, self.value)

    def __rpow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(other, self.value))
        else : return self.__class__(pow(other.value, self.value))

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


    def __iadd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __isub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __imul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __itruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __ifloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __imod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __idivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __ipow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __lt__(self, other) :
        if isinstance(other,(int,float)) : return self.value < other
        else : return self.value < other.value

    def __le__(self, other) :
        if isinstance(other,(int,float)) : return self.value <= other
        else : return self.value <= other.value

    def __eq__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value == other
        else : return self.value == other.value

    def __ne__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value != other
        else : return self.value != other.value

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
    
    def __invert__(self) :
        return self.__class__(~self.value)
        

    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return self.value
    
    def __float__(self) :
        return float(self.value)


    def __index__(self) :
        return self.value

    def __round__(self, ndigits) :
        return round(self.value,ndigits)
    
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


    def __hash__(self) :
        return self.value.__hash__()


class int16(ctypes.c_int16) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        my_super(int16,self).__init__(int(value))


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __truediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __floordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __mod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __divmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __pow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __radd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other + self.value)
        else : return self.__class__(other.value + self.value)

    def __rsub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other - self.value)
        else : return self.__class__(other.value - self.value)

    def __rmul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other * self.value)
        else : return self.__class__(other.value * self.value)

    def __rtruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other / self.value)
        else : return self.__class__(other.value / self.value)

    def __rfloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other // self.value)
        else : return self.__class__(other.value // self.value)

    def __rmod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other % self.value)
        else : return self.__class__(other.value % self.value)

    def __rdivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(other, self.value)
        else : return divmod(other.value, self.value)

    def __rpow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(other, self.value))
        else : return self.__class__(pow(other.value, self.value))

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


    def __iadd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __isub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __imul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __itruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __ifloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __imod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __idivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __ipow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __lt__(self, other) :
        if isinstance(other,(int,float)) : return self.value < other
        else : return self.value < other.value

    def __le__(self, other) :
        if isinstance(other,(int,float)) : return self.value <= other
        else : return self.value <= other.value

    def __eq__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value == other
        else : return self.value == other.value

    def __ne__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value != other
        else : return self.value != other.value

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
    
    def __invert__(self) :
        return self.__class__(~self.value)
        

    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return self.value
    
    def __float__(self) :
        return float(self.value)


    def __index__(self) :
        return self.value

    def __round__(self, ndigits) :
        return round(self.value,ndigits)
    
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


    def __hash__(self) :
        return self.value.__hash__()


class int32(ctypes.c_int32) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        my_super(int32,self).__init__(int(value))


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __truediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __floordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __mod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __divmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __pow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __radd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other + self.value)
        else : return self.__class__(other.value + self.value)

    def __rsub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other - self.value)
        else : return self.__class__(other.value - self.value)

    def __rmul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other * self.value)
        else : return self.__class__(other.value * self.value)

    def __rtruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other / self.value)
        else : return self.__class__(other.value / self.value)

    def __rfloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other // self.value)
        else : return self.__class__(other.value // self.value)

    def __rmod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other % self.value)
        else : return self.__class__(other.value % self.value)

    def __rdivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(other, self.value)
        else : return divmod(other.value, self.value)

    def __rpow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(other, self.value))
        else : return self.__class__(pow(other.value, self.value))

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


    def __iadd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __isub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __imul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __itruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __ifloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __imod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __idivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __ipow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __lt__(self, other) :
        if isinstance(other,(int,float)) : return self.value < other
        else : return self.value < other.value

    def __le__(self, other) :
        if isinstance(other,(int,float)) : return self.value <= other
        else : return self.value <= other.value

    def __eq__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value == other
        else : return self.value == other.value

    def __ne__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value != other
        else : return self.value != other.value

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
    
    def __invert__(self) :
        return self.__class__(~self.value)
        

    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return self.value
    
    def __float__(self) :
        return float(self.value)


    def __index__(self) :
        return self.value

    def __round__(self, ndigits) :
        return round(self.value,ndigits)
    
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


    def __hash__(self) :
        return self.value.__hash__()


class int64(ctypes.c_int64) :

    def __init__(self, value: Union[str,int,float] = ...) -> None:
        my_super(int64,self).__init__(int(value))


    def __add__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __sub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __mul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __truediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __floordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __mod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __divmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __pow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __radd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other + self.value)
        else : return self.__class__(other.value + self.value)

    def __rsub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other - self.value)
        else : return self.__class__(other.value - self.value)

    def __rmul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other * self.value)
        else : return self.__class__(other.value * self.value)

    def __rtruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(other / self.value)
        else : return self.__class__(other.value / self.value)

    def __rfloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other // self.value)
        else : return self.__class__(other.value // self.value)

    def __rmod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(other % self.value)
        else : return self.__class__(other.value % self.value)

    def __rdivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(other, self.value)
        else : return divmod(other.value, self.value)

    def __rpow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(other, self.value))
        else : return self.__class__(pow(other.value, self.value))

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
        if isinstance(other,(int)) : return self.__class__(self.value | other)
        else : return self.__class__(self.value | other.value)


    def __iadd__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value + other)
        else : return self.__class__(self.value + other.value)

    def __isub__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value - other)
        else : return self.__class__(self.value - other.value)

    def __imul__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value * other)
        else : return self.__class__(self.value * other.value)

    def __itruediv__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(self.value / other)
        else : return self.__class__(self.value / other.value)

    def __ifloordiv__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value // other)
        else : return self.__class__(self.value // other.value)

    def __imod__(self,other) :
        if isinstance(other,(int)) : return self.__class__(self.value % other)
        else : return self.__class__(self.value % other.value)

    def __idivmod__(self,other) :
        if isinstance(other,(int)) : return divmod(self.value,other)
        else : return divmod(self.value,other.value)

    def __ipow__(self,other) :
        if isinstance(other,(int,float)) : return self.__class__(pow(self.value , other))
        else : return self.__class__(pow(self.value , other.value))

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


    def __lt__(self, other) :
        if isinstance(other,(int,float)) : return self.value < other
        else : return self.value < other.value

    def __le__(self, other) :
        if isinstance(other,(int,float)) : return self.value <= other
        else : return self.value <= other.value

    def __eq__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value == other
        else : return self.value == other.value

    def __ne__(self, other) :
        if isinstance(other,(int,float,type(None))) : return self.value != other
        else : return self.value != other.value

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
    
    def __invert__(self) :
        return self.__class__(~self.value)
        

    def __complex__(self) :
        return complex(self.value,0)

    def __int__(self) :
        return self.value
    
    def __float__(self) :
        return float(self.value)


    def __index__(self) :
        return self.value

    def __round__(self, ndigits) :
        return round(self.value,ndigits)
    
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
    

    def __hash__(self) :
        return self.value.__hash__()



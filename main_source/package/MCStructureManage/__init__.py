from .. import python_nbt as nbt
from typing import Union

class TypeCheckList(list) :

    def setChecker(self, types:tuple) :
        if not isinstance(types, tuple) : types = (types, )
        self.Checker = types
        return self

    def append(self, value) :
        if not isinstance(value, self.Checker): 
            raise TypeError("添加的 %s 必须属于 %s 类型之一" % (value, self.Checker))
        return super().append(value)
    
    def insert(self, index:int, value) :
        if not isinstance(value, self.Checker): 
            raise TypeError("添加的 %s 必须属于 %s 类型之一" % (value, self.Checker))
        return super().insert(index, value)
    
    def extend(self, iterable) :
        def check(iter) :
            for value in iter :
                if not isinstance(value, self.Checker) : 
                    raise TypeError("添加的 %s 必须属于 %s 类型之一" % (value, self.Checker))
                else : yield value
        super().extend(check(iterable))

    def copy(self) :
        return self.__class__(self)

    def __setitem__(self, index:Union[slice, int], value) :
        if isinstance(index, slice) :
            if not all( isinstance(i, self.Checker) for i in value ) : 
                raise TypeError("设置值需要属于 %s 类型" % list(self.Checker))
        elif not isinstance(value, self.Checker): 
            raise TypeError("设置值需要属于 %s 类型" % list(self.Checker))
        return super().__setitem__(index, value)



from . import StructureBDX, StructureMCS
from .codec import Encoder, Decoder
from .structure import CommonStructure
"""
私有模块用于定义非暴露但是重要的自定义对象
"""
import itertools, struct, array
from typing import Dict,Any,Iterable,Union,List,Literal
array.array


class TypeCheckList(list) :
    from typing import Union

    def __init__(self, *args) :
        super().__init__(*args)
        self.Checker = None

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
        return self.__class__(self).setChecker(self.Checker)

    def __setitem__(self, index:Union[slice, int], value) :
        if isinstance(index, slice) :
            if not all( isinstance(i, self.Checker) for i in value ) : 
                raise TypeError("设置值需要属于 %s 类型" % list(self.Checker))
        elif not isinstance(value, self.Checker): 
            raise TypeError("设置值需要属于 %s 类型" % list(self.Checker))
        return super().__setitem__(index, value)

class BiList :

    def __init__(self, iterable:Iterable=[]) :
        self.__forward:List[Any] = list(iterable)
        self.__backward:Dict[Any, int] = {j:i for i,j in zip( reversed(self.__forward), 
            reversed( range(len(self.__forward)) ) )}


    def __str__(self) :
        return str(self.__forward)

    def __repr__(self):
        return f"<BiList Object id={id(self)}\n    list={self.__forward}\n    dict={self.__backward}\n>"


    def __iter__(self) :
        return self.__forward.__iter__()
    
    def __len__(self) :
        return len(self.__forward)

    def __getitem__(self, index:Any) :
        return self.__forward[index] if index.__class__ is int else self.__backward[index]

    def __setitem__(self, key:int, value:Any) :
        if key >= len(self.__forward) : raise IndexError(f'Key {key} out of index.')
        if value in self.__backward : return None
        if self.__forward[key] in self.__backward : del self.__backward[self.__forward[key]]
        self.__forward[key] = value
        self.__backward[value] = key

    def __delitem__(self, key:Union[int, Any]):
        if key.__class__ is int :
            del self.__backward[self.__forward[key]]
            del self.__forward[key]
        elif key in self.__backward :
            del self.__forward[self.__backward[key]]
            del self.__backward[key]
        else: raise KeyError(f'Key or value {key} not found.')
    

    def __add__(self, iter_obj: Iterable) :
        return self.__class__(self.__forward + list(iter_obj))

    def __iadd__(self, iter_obj: Iterable) :
        self.extend(iter_obj)

    def __mul__(self, value: int) :
        return self.__class__(self.__forward * value)

    def __rmul__(self, value: int) :
        return self.__class__(self.__forward * value)

    def __imul__(self, value: int) :
        return self.__class__(self.__forward * value)


    def __contains__(self, value:Any) :
        return value in self.__backward
    
    def __reversed__(self) :
        return self.__forward.__reversed__()


    def clear(self) :
        self.__forward.clear()
        self.__backward.clear()

    def copy(self) :
        self.__class__(self.__forward)

    def append(self, value:Any) :
        if value in self.__backward : return self.__backward[value]
        self.__backward[value] = len(self.__forward)
        self.__forward.append(value)
        return self.__backward[value]

    def insert(self, index:int, value:Any) :
        if value in self.__backward : return None
        self.__forward.insert(index, value)
        for i,j in zip(self.__forward[index:], itertools.count(index)) : 
            self.__backward[i] = j

    def extend(self, iterable:Iterable) :
        for value in iterable :
            if value in self.__backward : continue
            self.__backward[value] = len(self.__forward)
            self.__forward.append(value)

    def pop(self, index:int) :
        a = self.__forward.pop(index)
        del self.__backward[a]
        for i,j in zip(self.__forward[index:], itertools.count(index)) : 
            self.__backward[i] = j
        return a
        
    def remove(self, value:Any) :
        if value not in self.__backward : raise ValueError(f"object {value} not in list.")
        a = self.__backward[value]
        self.pop(a)
    
    def index(self, value:Any, start:int=0, stop:int=2**63-1) :
        return self.__forward.index(value, start, stop)


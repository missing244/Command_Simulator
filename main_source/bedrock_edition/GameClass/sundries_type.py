from . import MinecraftSimulator
from .item import ItemStack
from typing import List, Dict, Union, Literal, Tuple, TypedDict, Generator, Set, Optional

def bind_context(_context:MinecraftSimulator):
    """类装饰器：给类注入上下文"""
    def decorator(cls:type):

        class Wrapped(cls):

            context = _context
            create_count = 1

            def __init__(self, *args, **kwargs):
                if self.context is None:
                    raise RuntimeError(f"{cls.__name__} not initialized with context")
                super().__init__(*args, **kwargs)

        # 保留原始类的元信息
        Wrapped.__name__ = cls.__name__
        Wrapped.__doc__ = cls.__doc__
        return Wrapped
    
    return decorator

def iter_pos(startX:int, startZ:int, endX:int, endZ:int):
    endX_plus = endX + 1
    endZ_plus = endZ + 1
    x = (startX // 16) * 16
    while x < endX_plus:
        z = (startZ // 16) * 16
        while z < endZ_plus:
            x1 = x if x > startX else startX
            z1 = z if z > startZ else startZ
            x2 = x + 16
            if x2 > endX_plus: x2 = endX_plus
            z2 = z + 16
            if z2 > endZ_plus: z2 = endZ_plus
            yield (x1, z1, x2, z2)
            z += 16
        x += 16

class Container :

    def __init__(self) :
        self.Size = 0
        self.Items:List[Optional[ItemStack]] = []

    def __setattr__(self, name, value) :
        if  name == "Size" and hasattr(self, name) :
            if not isinstance(value, int) : raise TypeError("Container数量不能为非整数")
            if value > 100 : raise ValueError("Container数量不能超过100")
            if value < 0 : raise ValueError("Container数量不能为负数")
            temp1 = value - self.Size
            if temp1 > 0 : self.Items.extend(None for i in range(temp1))
            elif temp1 == 0 : pass
            else : del self.Items[temp1:]
        super().__setattr__(name, value)

    @property
    def EmptySlotsCount(self) -> int:
        return sum(1 for item in self.Items[:self.Size] if item is None)


    def add_item(self, item_stack:ItemStack) -> Optional[ItemStack]:
        """
        尝试将物品添加到容器。
        先尝试堆叠到已有物品，再放入空槽。
        返回未添加完成的 ItemStack（若全部添加则返回 None）。
        """
        if not isinstance(item_stack, ItemStack) : raise TypeError("item_stack传入了非物品堆叠对象")
        if item_stack.Count <= 0 : raise TypeError("item_stack传入了负数量物品堆叠对象")
        if any(self.Items[slot] is item_stack for slot in range(self.Size)) : return None   # 物品已在容器内，忽略本次调用

        # 1. 堆叠到已有物品
        for slot in range(self.Size):
            existing = self.Items[slot]
            if existing is None : continue
            if not existing.compatible_with(item_stack) : continue
            existing.stackable_with(item_stack)
            if item_stack.Count <= 0 : return None

        # 2. 放入空槽
        if item_stack.Count > 0:
            empty_slot = self.first_empty_slot()
            if empty_slot is None: return item_stack
            else: self.Items[empty_slot] = item_stack

        return None

    def clear_all(self) -> None:
        """清空所有槽位"""
        for i in range(self.Size): self.Items[i] = None

    def contains(self, item_stack:ItemStack) -> bool:
        """检查是否存在可堆叠的物品"""
        if not isinstance(item_stack, ItemStack) : raise TypeError("item_stack传参不是物品对象")
        return self.find(item_stack) is not None

    def find_last(self, item_stack:ItemStack) -> Optional[int]:
        """返回最后一个匹配物品的索引，未找到返回 None"""
        if not isinstance(item_stack, ItemStack) : raise TypeError("item_stack传参不是物品对象")
        for i in range(self.Size-1, -1, -1):
            item = self.Items[i]
            if item is None : continue
            if item.compatible_with(item_stack) : return i
        return None
    
    def find(self, item_stack:ItemStack, index:int=0) -> Optional[int]:
        """返回第一个匹配物品的索引，未找到返回 None"""
        if not isinstance(item_stack, ItemStack) : raise TypeError("item_stack传参不是物品对象")
        for i in range(max(0, index), self.Size):
            item = self.Items[i]
            if item is None : continue
            if item.compatible_with(item_stack) : return i
        return None

    def first_empty_slot(self, index:int=0) -> Optional[int]:
        """返回第一个空槽的索引，无空槽返回 None"""
        for i in range(max(0, index), self.Size):
            if self.Items[i] is None: return i
        return None

    def first_item(self, index:int=0) -> Optional[int]:
        """返回第一个非空槽的索引，全空返回 None"""
        for i in range(max(0, index), self.Size):
            if self.Items[i] is not None: return i
        return None

    def get_item(self, slot:int, deepcopy=True) -> Optional[ItemStack]:
        """获取指定槽位的物品引用（可能为 None）"""
        if slot < 0 or slot >= self.Size: raise IndexError("槽位索引超出范围")
        if deepcopy : return self.Items[slot].copy() if self.Items[slot] else None
        else : return self.Items[slot]

    def set_item(self, slot:int, item_stack:Optional[ItemStack]) -> None:
        """设置指定槽位的物品（可为 None）"""
        if not isinstance(item_stack, (ItemStack, type(None))) : raise TypeError("item_stack传参不是物品对象")
        if slot < 0 or slot >= self.Size: raise IndexError("槽位索引超出范围")
        self.Items[slot] = item_stack


import os, io, json, array
from .. import nbt
from ..__private import TypeCheckList
from typing import Union, List, Dict, Tuple
from io import FileIO, BytesIO

try :
    from ...Py_module import msgpack
except Exception :
    import msgpack


class BDS :
    """
    BDS 结构文件对象
    -----------------------
    * 管理 .bds 为后缀的 msgpack 结构文件
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构原点坐标(最小坐标)
    * 可用属性 block_index : 方块索引列表
    * 可用属性 block_palette : 调色盘对象列表
    * 可用属性 block_nbt : 以方块索引和nbt对象组成的字典
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数组或缓冲区生成对象
    * 可用方法 save_as : 通过路径或缓冲区保存对象数据
    """

    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.origin: array.array = array.array("i", [0, 0, 0])
        self.block_index: array.array = array.array("i")
        self.block_palette: List[dict] = TypeCheckList().setChecker(dict)
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")

    @classmethod
    def _read_bytes(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> bytes :
        if isinstance(buffer, str) :
            with open(buffer, "rb") as _f : return _f.read()
        if isinstance(buffer, bytes) : return buffer
        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() : buffer.seek(0)
            return buffer.read()
        raise TypeError(f"{buffer} 不是可读取对象")

    @classmethod
    def _write_bytes(cls, buffer:Union[str, FileIO, BytesIO], data:bytes) :
        if isinstance(buffer, str) :
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            with open(buffer, "wb") as _f :
                _f.write(data)
            return
        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() :
                buffer.seek(0)
                try : buffer.truncate(0)
                except : pass
            buffer.write(data)
            return
        raise TypeError(f"{buffer} 不是可写入对象")

    @classmethod
    def _safe_int(cls, value, default:int=0) -> int :
        try : return int(value)
        except : return default

    @classmethod
    def _normalize_name(cls, name) -> str :
        if not isinstance(name, str) : return "minecraft:air"
        name = name.strip()
        if not name : return "minecraft:air"
        return name if ":" in name else f"minecraft:{name}"

    @classmethod
    def _is_air_name(cls, name:str) -> bool :
        if not isinstance(name, str) : return True
        name = name.lower().strip()
        return name in ("air", "minecraft:air", "minecraft:void_air", "minecraft:cave_air")

    @classmethod
    def _normalize_states(cls, data) -> Tuple[dict, int, str] :
        if isinstance(data, dict) :
            state = {}
            for key, value in data.items() :
                key = str(key)
                if isinstance(value, (bool, int, float, str)) : state[key] = value
                else : state[key] = str(value)
            return state, 0, ""

        if isinstance(data, str) :
            text = data.strip()
            if not text : return {}, 0, ""
            if text.lstrip("+-").isdigit() : return {}, int(text), ""
            if text.startswith("[") and text.endswith("]") : return {}, 0, text
            return {}, 0, ""

        if isinstance(data, (int, float)) :
            return {}, int(data), ""

        return {}, 0, ""

    @classmethod
    def verify(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> bool :
        try :
            data = cls._read_bytes(buffer)
            obj = msgpack.unpackb(data, raw=False, strict_map_key=False)
        except :
            return False

        if not isinstance(obj, list) or len(obj) < 1 : return False
        if not isinstance(obj[0], list) or len(obj[0]) < 1 : return False

        block = obj[0][0]
        if not isinstance(block, list) : return False
        if len(block) not in (6, 7) : return False
        return True

    @classmethod
    def from_buffer(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        data = cls._read_bytes(buffer)
        obj = msgpack.unpackb(data, raw=False, strict_map_key=False)
        if not isinstance(obj, list) or len(obj) < 1 or not isinstance(obj[0], list) :
            raise ValueError("BDS文件结构无效")

        blocks = obj[0]
        min_x = min_y = min_z = 2147483647
        max_x = max_y = max_z = -2147483648
        has_pos = False

        for block in blocks :
            if not isinstance(block, list) or len(block) < 4 : continue
            x = cls._safe_int(block[1])
            y = cls._safe_int(block[2])
            z = cls._safe_int(block[3])
            min_x, min_y, min_z = min(min_x, x), min(min_y, y), min(min_z, z)
            max_x, max_y, max_z = max(max_x, x), max(max_y, y), max(max_z, z)
            has_pos = True

        if not has_pos : raise ValueError("BDS文件缺少坐标数据")

        size_x, size_y, size_z = max_x - min_x + 1, max_y - min_y + 1, max_z - min_z + 1
        ret = cls()
        ret.size = array.array("i", [size_x, size_y, size_z])
        ret.origin = array.array("i", [min_x, min_y, min_z])
        ret.block_index = array.array("i", [0] * (size_x * size_y * size_z))

        ret.block_palette.append({"name": "minecraft:air", "states": {}, "data": 0, "states_string": ""})
        palette_map:Dict[Tuple[str, str, int, str], int] = {
            ("minecraft:air", "{}", 0, "") : 0
        }

        for block in blocks :
            if not isinstance(block, list) or len(block) < 4 : continue
            name = cls._normalize_name(block[0] if len(block) >= 1 else "minecraft:air")
            x = cls._safe_int(block[1])
            y = cls._safe_int(block[2])
            z = cls._safe_int(block[3])
            data_field = block[4] if len(block) > 4 else 0
            is_air = bool(block[5]) if len(block) > 5 and isinstance(block[5], bool) else False

            if is_air or cls._is_air_name(name) :
                continue

            state, data_value, states_string = cls._normalize_states(data_field)
            key = (name, json.dumps(state, sort_keys=True, ensure_ascii=False), data_value, states_string)
            if key not in palette_map :
                palette_map[key] = len(ret.block_palette)
                ret.block_palette.append({
                    "name" : name,
                    "states" : state,
                    "data" : data_value,
                    "states_string" : states_string
                })
            palette_id = palette_map[key]

            rx, ry, rz = x - min_x, y - min_y, z - min_z
            if not (0 <= rx < size_x and 0 <= ry < size_y and 0 <= rz < size_z) :
                continue
            index = (rx * size_y + ry) * size_z + rz
            ret.block_index[index] = palette_id

        return ret

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        size_x, size_y, size_z = self.size[0], self.size[1], self.size[2]
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("结构尺寸无效")

        blocks = []
        for index, palette_id in enumerate(self.block_index) :
            if palette_id <= 0 or palette_id >= len(self.block_palette) : continue
            block = self.block_palette[palette_id]
            name = self._normalize_name(block.get("name", "minecraft:air"))
            if self._is_air_name(name) : continue

            x = index // (size_y * size_z)
            y = (index % (size_y * size_z)) // size_z
            z = index % size_z

            states = block.get("states", {})
            data_value = self._safe_int(block.get("data", 0), 0)
            states_string = block.get("states_string", "")

            if states_string : data_field = states_string
            elif isinstance(states, dict) and states : data_field = dict(states)
            else : data_field = data_value

            blocks.append([name, int(x), int(y), int(z), data_field, False])

        blocks.append(["minecraft:air", 0, 0, 0, 0, True])
        corner = [size_x - 1, size_y - 1, size_z - 1]
        if corner != [0, 0, 0] :
            blocks.append(["minecraft:air", corner[0], corner[1], corner[2], 0, True])

        out = [blocks]
        data = msgpack.packb(out, use_bin_type=True)
        self._write_bytes(buffer, data)

import os, io, json, array
from .. import nbt
from ..__private import TypeCheckList
from typing import Union, List, Dict, Tuple
from io import FileIO, BytesIO


class CovStructure :
    """
    CovStructure 结构文件对象
    -----------------------
    * 管理 .covstructure 为后缀的 json 结构文件
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构原点坐标(最小坐标)
    * 可用属性 block_index : 方块索引列表
    * 可用属性 block_palette : 调色盘对象列表
    * 可用属性 block_nbt : 以方块索引和nbt对象组成的字典
    * 可用属性 entity_nbt : 实体NBT对象列表
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
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")

    @classmethod
    def _read_text(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> str :
        if isinstance(buffer, str) :
            with open(buffer, "r", encoding="utf-8") as _f : return _f.read()
        if isinstance(buffer, bytes) : return buffer.decode("utf-8", "ignore")
        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() : buffer.seek(0)
            data = buffer.read()
            if isinstance(data, bytes) : return data.decode("utf-8", "ignore")
            return str(data)
        raise TypeError(f"{buffer} 不是可读取对象")


    @classmethod
    def _load_json(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        if isinstance(buffer, bytes) :
            return json.loads(buffer.decode("utf-8", "ignore"))

        if isinstance(buffer, str) :
            with open(buffer, "r", encoding="utf-8") as f :
                return json.load(f)

        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() : buffer.seek(0)
            if isinstance(buffer, io.TextIOBase) :
                return json.load(buffer)
            data = buffer.read()
            if isinstance(data, bytes) :
                return json.loads(data.decode("utf-8", "ignore"))
            return json.loads(str(data))

        raise TypeError(f"{buffer} 不是可读取对象")

    @classmethod
    def _write_text(cls, buffer:Union[str, FileIO, BytesIO], data:str) :
        if isinstance(buffer, str) :
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            with open(buffer, "w", encoding="utf-8") as _f :
                _f.write(data)
            return
        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() :
                buffer.seek(0)
                try : buffer.truncate(0)
                except : pass

            if "b" in getattr(buffer, "mode", "") : buffer.write(data.encode("utf-8"))
            else : buffer.write(data)
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
    def _normalize_states(cls, states) -> dict :
        if not isinstance(states, dict) : return {}
        ret = {}
        for key, value in states.items() :
            key = str(key)
            if isinstance(value, (bool, int, float, str)) : ret[key] = value
            else : ret[key] = str(value)
        return ret

    @classmethod
    def _tag_to_value(cls, tag_obj):
        if isinstance(tag_obj, nbt.TAG_Byte) :
            value = tag_obj.get_value()
            return bool(value) if value in (0, 1) else value
        if isinstance(tag_obj, (nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) :
            return tag_obj.get_value()
        if isinstance(tag_obj, (nbt.TAG_Float, nbt.TAG_Double)) :
            return tag_obj.get_value()
        if isinstance(tag_obj, nbt.TAG_String) :
            return tag_obj.get_value()
        if isinstance(tag_obj, nbt.TAG_ByteArray) :
            return bytes((v & 0xff) for v in tag_obj.get_value())
        if isinstance(tag_obj, nbt.TAG_IntArray) :
            return [int(v) for v in tag_obj.get_value()]
        if isinstance(tag_obj, nbt.TAG_LongArray) :
            return [int(v) for v in tag_obj.get_value()]
        if isinstance(tag_obj, nbt.TAG_List) :
            return [cls._tag_to_value(i) for i in tag_obj]
        if isinstance(tag_obj, nbt.TAG_Compound) :
            return {k: cls._tag_to_value(v) for k, v in tag_obj.items()}
        return None

    @classmethod
    def _value_to_tag(cls, value):
        if isinstance(value, bool) : return nbt.TAG_Byte(int(value))
        if isinstance(value, int) : return nbt.TAG_Int(value)
        if isinstance(value, float) : return nbt.TAG_Double(value)
        if isinstance(value, str) : return nbt.TAG_String(value)
        if isinstance(value, bytes) : return nbt.TAG_ByteArray(array.array("b", value))
        if isinstance(value, list) :
            list_tag = nbt.TAG_List()
            for item in value :
                item_tag = cls._value_to_tag(item)
                if item_tag is None : continue
                list_tag.append(item_tag)
            return list_tag
        if isinstance(value, dict) :
            cmp_tag = nbt.TAG_Compound()
            for key, val in value.items() :
                val_tag = cls._value_to_tag(val)
                if val_tag is None : continue
                cmp_tag[str(key)] = val_tag
            return cmp_tag
        return None

    @classmethod
    def verify(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> bool :
        try :
            data = cls._load_json(buffer)
        except :
            return False

        if not isinstance(data, dict) : return False
        size = data.get("size", data.get("dimensions", None))
        if not (isinstance(size, list) and len(size) >= 3) : return False

        if "structure" in data and isinstance(data["structure"], dict) :
            st = data["structure"]
            if "block_indices" in st or "blocks" in st : return True
            return False

        return ("block_indices" in data or "blocks" in data)

    @classmethod
    def from_buffer(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        data = cls._load_json(buffer)
        if not isinstance(data, dict) : raise ValueError("CovStructure根对象不是json对象")

        size = data.get("size", data.get("dimensions", None))
        if not (isinstance(size, list) and len(size) >= 3) :
            raise ValueError("CovStructure缺少size字段")

        size_x, size_y, size_z = cls._safe_int(size[0]), cls._safe_int(size[1]), cls._safe_int(size[2])
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("CovStructure尺寸无效")

        st = data.get("structure", data)
        if not isinstance(st, dict) : raise ValueError("CovStructure结构对象无效")

        block_indices = st.get("block_indices", st.get("blocks", []))
        layer0, layer1 = [], []
        if isinstance(block_indices, list) and len(block_indices) > 0 and isinstance(block_indices[0], list) :
            layer0 = block_indices[0]
            if len(block_indices) > 1 and isinstance(block_indices[1], list) : layer1 = block_indices[1]
        elif isinstance(block_indices, list) :
            layer0 = block_indices
        else :
            raise ValueError("CovStructure block_indices无效")

        palette_raw = []
        block_position_data = {}
        palette_data = st.get("palette", [])
        if isinstance(palette_data, dict) :
            default = palette_data.get("default", palette_data)
            if isinstance(default, dict) :
                palette_raw = default.get("block_palette", [])
                if isinstance(default.get("block_position_data", None), dict) :
                    block_position_data = default.get("block_position_data", {})
        elif isinstance(palette_data, list) :
            palette_raw = palette_data

        ret = cls()
        ret.size = array.array("i", [size_x, size_y, size_z])

        origin = data.get("structure_world_origin", [0, 0, 0])
        if isinstance(origin, list) and len(origin) >= 3 :
            ret.origin = array.array("i", [cls._safe_int(origin[0]), cls._safe_int(origin[1]), cls._safe_int(origin[2])])

        volume = size_x * size_y * size_z
        ret.block_index = array.array("i", [0] * volume)

        parsed_palette = []
        value_to_entry = {}
        for index, pal in enumerate(palette_raw if isinstance(palette_raw, list) else []) :
            if not isinstance(pal, dict) : continue
            name = cls._normalize_name(pal.get("name", pal.get("Name", "minecraft:air")))
            states = cls._normalize_states(pal.get("states", pal.get("Properties", {})))
            val = cls._safe_int(pal.get("val", index), index)
            parsed_palette.append({
                "name" : name,
                "states" : states,
                "val" : val,
                "version" : cls._safe_int(pal.get("version", 17959425), 17959425)
            })
            value_to_entry[val] = parsed_palette[-1]

        if not parsed_palette :
            parsed_palette = [{"name":"minecraft:air", "states":{}, "val":0, "version":17959425}]
            value_to_entry[0] = parsed_palette[0]

        ret.block_palette.append({"name":"minecraft:air", "states":{}, "val":0, "version":17959425})
        palette_map:Dict[Tuple[str, str], int] = {
            ("minecraft:air", "{}") : 0
        }

        for index in range(volume) :
            value = cls._safe_int(layer0[index], 0) if index < len(layer0) else 0
            pal = value_to_entry.get(value, None)
            if pal is None and 0 <= value < len(parsed_palette) : pal = parsed_palette[value]
            if pal is None : pal = {"name":"minecraft:air", "states":{}, "val":0, "version":17959425}

            name = cls._normalize_name(pal.get("name", "minecraft:air"))
            states = cls._normalize_states(pal.get("states", {}))
            key = (name, json.dumps(states, sort_keys=True, ensure_ascii=False))
            if key not in palette_map :
                palette_map[key] = len(ret.block_palette)
                ret.block_palette.append({
                    "name" : name,
                    "states" : states,
                    "val" : len(ret.block_palette),
                    "version" : cls._safe_int(pal.get("version", 17959425), 17959425)
                })
            ret.block_index[index] = palette_map[key]

        for idx_str, payload in block_position_data.items() :
            try : pos_idx = int(idx_str)
            except : continue
            if not (0 <= pos_idx < volume) : continue

            if isinstance(payload, dict) and isinstance(payload.get("block_entity_data", None), dict) :
                payload = payload["block_entity_data"]
            if not isinstance(payload, dict) : continue

            tag = cls._value_to_tag(payload)
            if isinstance(tag, nbt.TAG_Compound) : ret.block_nbt[pos_idx] = tag

        entities = st.get("entities", [])
        if isinstance(entities, list) :
            for entity in entities :
                if not isinstance(entity, dict) : continue
                tag = cls._value_to_tag(entity)
                if isinstance(tag, nbt.TAG_Compound) : ret.entity_nbt.append(tag)

        return ret

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        size_x, size_y, size_z = self.size[0], self.size[1], self.size[2]
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("结构尺寸无效")

        volume = size_x * size_y * size_z
        layer0 = [0] * volume
        layer1 = [-1] * volume
        for index in range(min(volume, len(self.block_index))) :
            layer0[index] = int(self.block_index[index])

        palette_list = []
        for index, block in enumerate(self.block_palette) :
            name = self._normalize_name(block.get("name", "minecraft:air"))
            states = self._normalize_states(block.get("states", {}))
            palette_list.append({
                "name" : name,
                "states" : states,
                "val" : index,
                "version" : self._safe_int(block.get("version", 17959425), 17959425)
            })

        block_position_data = {}
        for index, block_nbt in self.block_nbt.items() :
            if not isinstance(index, int) : continue
            if not isinstance(block_nbt, nbt.TAG_Compound) : continue
            block_position_data[str(index)] = {
                "block_entity_data" : self._tag_to_value(block_nbt)
            }

        entities = [self._tag_to_value(i) for i in self.entity_nbt if isinstance(i, nbt.TAG_Compound)]

        obj = {
            "format_version" : 1,
            "size" : [int(size_x), int(size_y), int(size_z)],
            "structure" : {
                "block_indices" : [layer0, layer1],
                "entities" : entities,
                "palette" : {
                    "default" : {
                        "block_palette" : palette_list,
                        "block_position_data" : block_position_data
                    }
                }
            },
            "structure_world_origin" : [int(self.origin[0]), int(self.origin[1]), int(self.origin[2])]
        }

        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        self._write_text(buffer, text)

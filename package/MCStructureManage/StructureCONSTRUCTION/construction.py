import os, io, gzip, zlib, struct, array
from .. import nbt
from ..__private import TypeCheckList
from typing import Union, List, Dict, Tuple
from io import FileIO, BytesIO


class Construction :
    """
    Construction 结构文件对象
    -----------------------
    * 管理 .construction 为后缀的二进制结构文件
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

    MAGIC = b"constrct"

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
    def _open_reader(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        if isinstance(buffer, str) :
            return open(buffer, "rb"), True
        if isinstance(buffer, bytes) :
            return io.BytesIO(buffer), True
        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() : buffer.seek(0)
            return buffer, False
        raise TypeError(f"{buffer} 不是可读取对象")

    @classmethod
    def _read_range(cls, reader:io.IOBase, start:int, length:int, error_text:str) -> bytes :
        if start < 0 or length < 0 : raise ValueError(error_text)
        reader.seek(start)
        data = reader.read(length)
        if not isinstance(data, (bytes, bytearray)) or len(data) != length :
            raise ValueError(error_text)
        return bytes(data)

    @classmethod
    def _read_file_layout(cls, reader:io.IOBase) -> Tuple[int, int, int] :
        file_size = reader.seek(0, io.SEEK_END)
        min_size = len(cls.MAGIC) * 2 + 5
        if file_size < min_size : raise ValueError("Construction文件长度无效")

        head = cls._read_range(reader, 0, len(cls.MAGIC) + 1, "Construction头部损坏")
        if head[:len(cls.MAGIC)] != cls.MAGIC : raise ValueError("不是合法的 Construction 文件")
        if head[len(cls.MAGIC)] != 0 : raise ValueError("Construction头部版本非法")

        tail_magic = cls._read_range(reader, file_size - len(cls.MAGIC), len(cls.MAGIC), "Construction尾部损坏")
        if tail_magic != cls.MAGIC : raise ValueError("Construction尾部标识无效")

        metadata_end = file_size - len(cls.MAGIC) - 4
        metadata_start = struct.unpack(">I", cls._read_range(reader, metadata_end, 4, "Construction元数据索引损坏"))[0]
        if not (0 <= metadata_start < metadata_end) : raise ValueError("Construction元数据偏移无效")
        return file_size, metadata_start, metadata_end

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
    def _nbt_to_bytes(cls, tag:nbt.TAG_Compound, byteorder: str = "big") -> bytes :
        mem = io.BytesIO()
        nbt.write_to_nbt_file(mem, tag, zip_mode="none", byteorder=byteorder)
        return mem.getvalue()

    @classmethod
    def verify(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> bool :
        reader, need_close = None, False
        try :
            reader, need_close = cls._open_reader(buffer)
            if not reader.seekable() :
                reader = io.BytesIO(reader.read())
                need_close = True
            cls._read_file_layout(reader)
            return True
        except : return False
        finally :
            if need_close and reader is not None :
                try : reader.close()
                except : pass

    @classmethod
    def _decompress_bytes(cls, data:bytes) -> bytes :
        if len(data) >= 2 and data[0] == 0x1f and data[1] == 0x8b :
            try : return gzip.decompress(data)
            except : pass
        if len(data) >= 2 :
            try : return zlib.decompress(data)
            except : pass
        return data

    @classmethod
    def _safe_int(cls, value) -> int :
        if isinstance(value, bool) : return int(value)
        if isinstance(value, int) : return value
        if isinstance(value, float) : return int(value)
        raise TypeError("不是数字")

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
            comp = nbt.TAG_Compound()
            for k, v in value.items() :
                if not isinstance(k, str) : continue
                tag_obj = cls._value_to_tag(v)
                if tag_obj is None : continue
                comp[k] = tag_obj
            return comp
        return None

    @classmethod
    def _parse_bounds(cls, selection_boxes:List[int], section_list:List[Tuple[int,int,int,int,int,int,int,int]]) :
        if len(selection_boxes) >= 6 and len(selection_boxes) % 6 == 0 :
            min_x, min_y, min_z = selection_boxes[0], selection_boxes[1], selection_boxes[2]
            max_x, max_y, max_z = selection_boxes[3], selection_boxes[4], selection_boxes[5]
            for i in range(0, len(selection_boxes), 6) :
                min_x = min(min_x, selection_boxes[i+0])
                min_y = min(min_y, selection_boxes[i+1])
                min_z = min(min_z, selection_boxes[i+2])
                max_x = max(max_x, selection_boxes[i+3])
                max_y = max(max_y, selection_boxes[i+4])
                max_z = max(max_z, selection_boxes[i+5])
        else :
            min_x, min_y, min_z = 2**31-1, 2**31-1, 2**31-1
            max_x, max_y, max_z = -2**31, -2**31, -2**31
            for start_x, start_y, start_z, shape_x, shape_y, shape_z, _, _ in section_list :
                if shape_x <= 0 or shape_y <= 0 or shape_z <= 0 : continue
                min_x = min(min_x, start_x)
                min_y = min(min_y, start_y)
                min_z = min(min_z, start_z)
                max_x = max(max_x, start_x + shape_x)
                max_y = max(max_y, start_y + shape_y)
                max_z = max(max_z, start_z + shape_z)

        if max_x <= min_x or max_y <= min_y or max_z <= min_z :
            raise ValueError("Construction 文件缺少有效尺寸信息")
        return min_x, min_y, min_z, max_x, max_y, max_z

    @classmethod
    def _parse_section_index_table(cls, sit:nbt.TAG_ByteArray):
        raw = sit.get_value().tobytes()
        if len(raw) == 0 or len(raw) % 23 != 0 :
            raise ValueError("section_index_table 格式错误")

        section_list = []
        for i in range(0, len(raw), 23) :
            start_x, start_y, start_z = struct.unpack("<iii", raw[i:i+12])
            shape_x, shape_y, shape_z = raw[i+12], raw[i+13], raw[i+14]
            data_start, data_length = struct.unpack("<ii", raw[i+15:i+23])
            section_list.append((start_x, start_y, start_z, shape_x, shape_y, shape_z, data_start, data_length))
        return section_list

    @classmethod
    def _parse_section_blocks(cls, section_nbt:nbt.TAG_Compound) -> List[int] :
        if "blocks" not in section_nbt : return []

        array_type = -1
        if "blocks_array_type" in section_nbt and isinstance(section_nbt["blocks_array_type"], nbt.TAG_Byte) :
            array_type = section_nbt["blocks_array_type"].get_value()

        blocks_obj = section_nbt["blocks"]
        if array_type == 11 and isinstance(blocks_obj, nbt.TAG_IntArray) :
            return [int(v) for v in blocks_obj.get_value()]
        if array_type == 12 and isinstance(blocks_obj, nbt.TAG_LongArray) :
            return [int(v) for v in blocks_obj.get_value()]
        if array_type == 7 and isinstance(blocks_obj, nbt.TAG_ByteArray) :
            return [v & 0xff for v in blocks_obj.get_value()]

        if isinstance(blocks_obj, nbt.TAG_IntArray) :
            return [int(v) for v in blocks_obj.get_value()]
        if isinstance(blocks_obj, nbt.TAG_LongArray) :
            return [int(v) for v in blocks_obj.get_value()]
        if isinstance(blocks_obj, nbt.TAG_ByteArray) :
            return [v & 0xff for v in blocks_obj.get_value()]
        return []

    @classmethod
    def _to_root_compound(cls, data:bytes) -> nbt.TAG_Compound :
        root = nbt.read_from_nbt_file(io.BytesIO(data), byteorder="big").get_tag()
        if not isinstance(root, nbt.TAG_Compound) :
            raise ValueError("NBT 根标签不是 TAG_Compound")
        return root


    @classmethod
    def from_buffer(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        reader, need_close = cls._open_reader(buffer)
        try :
            if not reader.seekable() :
                reader = io.BytesIO(reader.read())
                need_close = True

            file_size, metadata_start, metadata_end = cls._read_file_layout(reader)
            metadata = cls._decompress_bytes(cls._read_range(
                reader, metadata_start, metadata_end - metadata_start, "Construction元数据损坏"))
            metadata_nbt = cls._to_root_compound(metadata)

            if "section_index_table" not in metadata_nbt or not isinstance(metadata_nbt["section_index_table"], nbt.TAG_ByteArray) :
                raise ValueError("Construction 缺少 section_index_table")
            if "block_palette" not in metadata_nbt or not isinstance(metadata_nbt["block_palette"], nbt.TAG_List) :
                raise ValueError("Construction 缺少 block_palette")

            selection_boxes = []
            if "selection_boxes" in metadata_nbt and isinstance(metadata_nbt["selection_boxes"], nbt.TAG_IntArray) :
                selection_boxes = [int(v) for v in metadata_nbt["selection_boxes"].get_value()]

            section_list = cls._parse_section_index_table(metadata_nbt["section_index_table"])
            min_x, min_y, min_z, max_x, max_y, max_z = cls._parse_bounds(selection_boxes, section_list)
            size_x, size_y, size_z = max_x - min_x, max_y - min_y, max_z - min_z

            obj = cls()
            obj.size = array.array("i", [size_x, size_y, size_z])
            obj.origin = array.array("i", [min_x, min_y, min_z])
            obj.block_index = array.array("i", [0] * (size_x * size_y * size_z))

            for palette_entry in metadata_nbt["block_palette"] :
                if not isinstance(palette_entry, nbt.TAG_Compound) :
                    obj.block_palette.append({"namespace":"minecraft", "blockname":"unknown", "properties":{}})
                    continue

                namespace = "minecraft"
                blockname = "unknown"
                properties = {}

                if "namespace" in palette_entry and isinstance(palette_entry["namespace"], nbt.TAG_String) :
                    namespace = palette_entry["namespace"].get_value() or "minecraft"
                if "blockname" in palette_entry and isinstance(palette_entry["blockname"], nbt.TAG_String) :
                    blockname = palette_entry["blockname"].get_value() or "unknown"
                if "properties" in palette_entry and isinstance(palette_entry["properties"], nbt.TAG_Compound) :
                    for k, v in palette_entry["properties"].items() :
                        value = cls._tag_to_value(v)
                        if isinstance(value, (bool, int, str)) : properties[k] = value

                obj.block_palette.append({
                    "namespace": namespace,
                    "blockname": blockname,
                    "properties": properties,
                })

            if len(obj.block_palette) == 0 :
                obj.block_palette.append({"namespace":"minecraft", "blockname":"air", "properties":{}})

            y_z_size = size_y * size_z
            for start_x, start_y, start_z, shape_x, shape_y, shape_z, data_start, data_length in section_list :
                if shape_x <= 0 or shape_y <= 0 or shape_z <= 0 : continue
                if data_start < 0 or data_length <= 0 or data_start + data_length > file_size : continue

                section_data = cls._decompress_bytes(cls._read_range(
                    reader, data_start, data_length, "Construction区块数据损坏"))
                try : section_nbt = cls._to_root_compound(section_data)
                except : continue

                blocks = cls._parse_section_blocks(section_nbt)
                if blocks :
                    max_count = shape_x * shape_y * shape_z
                    section_y_z_size = shape_y * shape_z
                    for ptr, palette_index in enumerate(blocks) :
                        if ptr >= max_count : break
                        palette_index = cls._safe_int(palette_index)
                        if not (0 <= palette_index < len(obj.block_palette)) : palette_index = 0

                        local_x = ptr // section_y_z_size
                        local_y = (ptr % section_y_z_size) // shape_z
                        local_z = ptr % shape_z

                        world_x = start_x + local_x - min_x
                        world_y = start_y + local_y - min_y
                        world_z = start_z + local_z - min_z
                        if not (0 <= world_x < size_x and 0 <= world_y < size_y and 0 <= world_z < size_z) : continue

                        index = (world_x * size_y + world_y) * size_z + world_z
                        obj.block_index[index] = palette_index

                if "block_entities" not in section_nbt or not isinstance(section_nbt["block_entities"], nbt.TAG_List) :
                    continue

                for block_entity in section_nbt["block_entities"] :
                    if not isinstance(block_entity, nbt.TAG_Compound) : continue
                    if not("x" in block_entity and "y" in block_entity and "z" in block_entity) : continue
                    if not isinstance(block_entity["x"], (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : continue
                    if not isinstance(block_entity["y"], (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : continue
                    if not isinstance(block_entity["z"], (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : continue

                    world_x = block_entity["x"].get_value() - min_x
                    world_y = block_entity["y"].get_value() - min_y
                    world_z = block_entity["z"].get_value() - min_z
                    if not (0 <= world_x < size_x and 0 <= world_y < size_y and 0 <= world_z < size_z) : continue

                    if "nbt" in block_entity and isinstance(block_entity["nbt"], nbt.TAG_Compound) :
                        entity_nbt = block_entity["nbt"].copy()
                    else :
                        entity_nbt = nbt.TAG_Compound()

                    index = (world_x * y_z_size + world_y * size_z + world_z)
                    obj.block_nbt[index] = entity_nbt

            return obj
        finally :
            if need_close :
                try : reader.close()
                except : pass

    @classmethod
    def _split_block_id(cls, block_id:str) -> Tuple[str, str] :
        if ":" in block_id : return block_id.split(":", 1)
        return "minecraft", block_id

    @classmethod
    def _block_entity_namespace(cls, block_nbt:nbt.TAG_Compound, fallback_block:str) -> Tuple[str, str] :
        ns, base = cls._split_block_id(fallback_block)
        if "id" in block_nbt and isinstance(block_nbt["id"], nbt.TAG_String) :
            block_id = block_nbt["id"].get_value()
            if block_id :
                if ":" in block_id : return block_id.split(":", 1)
                return "", block_id
        return ns, base

    @classmethod
    def _section_pos_to_index(cls, x:int, y:int, z:int, size_y:int, size_z:int) -> int :
        return (x * size_y + y) * size_z + z

    def _encode_palette_entries(self) -> nbt.TAG_List :
        palette_list = nbt.TAG_List(type=nbt.TAG_Compound)
        for palette in self.block_palette :
            namespace = str(palette.get("namespace", "minecraft"))
            blockname = str(palette.get("blockname", "unknown"))
            properties = palette.get("properties", {})
            if not isinstance(properties, dict) : properties = {}

            prop_comp = nbt.TAG_Compound()
            for key, value in properties.items() :
                if not isinstance(key, str) : continue
                tag_obj = self._value_to_tag(value)
                if tag_obj is None : continue
                prop_comp[key] = tag_obj

            palette_comp = nbt.TAG_Compound()
            palette_comp["namespace"] = nbt.TAG_String(namespace)
            palette_comp["blockname"] = nbt.TAG_String(blockname)
            palette_comp["properties"] = prop_comp
            palette_comp["extra_blocks"] = nbt.TAG_List()
            palette_list.append(palette_comp)
        return palette_list

    def _build_section_entities(self) -> Dict[Tuple[int,int,int], nbt.TAG_List] :
        size_x, size_y, size_z = self.size
        entities_map:Dict[Tuple[int,int,int], nbt.TAG_List] = {}

        for index, be_nbt in self.block_nbt.items() :
            if not isinstance(index, int) : continue
            if not isinstance(be_nbt, nbt.TAG_Compound) : continue
            if index < 0 or index >= len(self.block_index) : continue

            x = index // (size_y * size_z)
            y = (index % (size_y * size_z)) // size_z
            z = index % size_z

            sec_key = (x//16*16, y//16*16, z//16*16)
            if sec_key not in entities_map :
                entities_map[sec_key] = nbt.TAG_List(type=nbt.TAG_Compound)

            block_palette_index = self.block_index[index]
            fallback_id = "minecraft:air"
            if 0 <= block_palette_index < len(self.block_palette) :
                p = self.block_palette[block_palette_index]
                fallback_id = "%s:%s" % (p.get("namespace", "minecraft"), p.get("blockname", "air"))
            namespace, base_name = self._block_entity_namespace(be_nbt, fallback_id)

            abs_x = self.origin[0] + x
            abs_y = self.origin[1] + y
            abs_z = self.origin[2] + z

            nbt_copy = be_nbt.copy()
            nbt_copy["x"] = nbt.TAG_Int(abs_x)
            nbt_copy["y"] = nbt.TAG_Int(abs_y)
            nbt_copy["z"] = nbt.TAG_Int(abs_z)

            entity_comp = nbt.TAG_Compound()
            entity_comp["namespace"] = nbt.TAG_String(namespace)
            entity_comp["base_name"] = nbt.TAG_String(base_name)
            entity_comp["x"] = nbt.TAG_Int(abs_x)
            entity_comp["y"] = nbt.TAG_Int(abs_y)
            entity_comp["z"] = nbt.TAG_Int(abs_z)
            entity_comp["nbt"] = nbt_copy
            entities_map[sec_key].append(entity_comp)

        return entities_map

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        size_x, size_y, size_z = [int(v) for v in self.size]
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("size 不是合法结构尺寸")

        volume = size_x * size_y * size_z
        if len(self.block_index) != volume :
            raise ValueError("block_index 长度与结构体积不一致")

        if len(self.block_palette) == 0 :
            self.block_palette.append({"namespace":"minecraft", "blockname":"air", "properties":{}})

        for i, index in enumerate(self.block_index) :
            if not (0 <= index < len(self.block_palette)) : self.block_index[i] = 0

        section_entities = self._build_section_entities()
        output = io.BytesIO()
        output.write(self.MAGIC)
        output.write(b"\x00")

        section_index_list = []
        for sec_x in range(0, size_x, 16) :
            shape_x = min(16, size_x - sec_x)
            for sec_y in range(0, size_y, 16) :
                shape_y = min(16, size_y - sec_y)
                for sec_z in range(0, size_z, 16) :
                    shape_z = min(16, size_z - sec_z)

                    blocks = array.array("i", [0] * (shape_x * shape_y * shape_z))
                    for x in range(shape_x) :
                        gx = sec_x + x
                        for y in range(shape_y) :
                            gy = sec_y + y
                            for z in range(shape_z) :
                                gz = sec_z + z
                                global_index = self._section_pos_to_index(gx, gy, gz, size_y, size_z)
                                ptr = self._section_pos_to_index(x, y, z, shape_y, shape_z)
                                blocks[ptr] = int(self.block_index[global_index])

                    section_nbt = nbt.TAG_Compound()
                    section_nbt["blocks_array_type"] = nbt.TAG_Byte(11)
                    section_nbt["blocks"] = nbt.TAG_IntArray(blocks)
                    section_nbt["block_entities"] = section_entities.get((sec_x, sec_y, sec_z), nbt.TAG_List(type=nbt.TAG_Compound))

                    section_raw = self._nbt_to_bytes(section_nbt, byteorder="big")
                    section_compressed = gzip.compress(section_raw)

                    section_pos = output.tell()
                    output.write(section_compressed)
                    section_index_list.append((
                        self.origin[0] + sec_x, self.origin[1] + sec_y, self.origin[2] + sec_z,
                        shape_x, shape_y, shape_z,
                        section_pos, len(section_compressed)
                    ))

        section_index_raw = bytearray()
        for start_x, start_y, start_z, shape_x, shape_y, shape_z, data_pos, data_len in section_index_list :
            section_index_raw.extend(struct.pack("<iiiBBBii", start_x, start_y, start_z, shape_x, shape_y, shape_z, data_pos, data_len))

        metadata = nbt.TAG_Compound()
        metadata["selection_boxes"] = nbt.TAG_IntArray(array.array("i", [
            self.origin[0], self.origin[1], self.origin[2],
            self.origin[0] + size_x, self.origin[1] + size_y, self.origin[2] + size_z
        ]))
        metadata["block_palette"] = self._encode_palette_entries()
        metadata["section_index_table"] = nbt.TAG_ByteArray(array.array("b", bytes(section_index_raw)))
        metadata["section_version"] = nbt.TAG_Byte(0)

        metadata_raw = self._nbt_to_bytes(metadata, byteorder="big")
        metadata_compressed = gzip.compress(metadata_raw)

        metadata_offset = output.tell()
        output.write(metadata_compressed)
        output.write(struct.pack(">I", metadata_offset))
        output.write(self.MAGIC)

        self._write_bytes(buffer, output.getvalue())

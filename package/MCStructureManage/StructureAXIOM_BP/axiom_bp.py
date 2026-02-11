import os, io, gzip, struct, array
from .. import nbt
from ..__private import TypeCheckList
from typing import Union, List, Dict, Tuple
from io import FileIO, BytesIO


class AxiomBP :
    """
    AxiomBP 结构文件对象
    -----------------------
    * 管理 .bp(axiom_bp) 格式结构文件
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构原点坐标(16对齐)
    * 可用属性 block_index : 方块索引列表
    * 可用属性 block_palette : 调色盘对象列表（Java Name/Properties）
    * 可用属性 block_nbt : 以方块索引和nbt对象组成的字典
    * 可用属性 entity_nbt : 实体对象列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数组或缓冲区生成对象
    * 可用方法 save_as : 通过路径或缓冲区保存对象数据
    """

    MAGIC = 0x0AE5BB36
    JAVA_DATA_VERSION = 4556
    AIR_NAME_SET = {"minecraft:air", "minecraft:void_air", "minecraft:cave_air"}

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
    def _nbt_to_bytes(cls, tag:nbt.TAG_Compound, byteorder: str = "big") -> bytes :
        mem = io.BytesIO()
        nbt.write_to_nbt_file(mem, tag, zip_mode="none", byteorder=byteorder)
        return mem.getvalue()

    @classmethod
    def _read_i32be(cls, data:bytes, offset:int) -> Tuple[int, int] :
        if offset + 4 > len(data) : raise ValueError("AxiomBP文件不完整")
        return struct.unpack(">i", data[offset:offset+4])[0], offset + 4

    @classmethod
    def _read_byte_array(cls, data:bytes, offset:int) -> Tuple[bytes, int] :
        arr_len, offset = cls._read_i32be(data, offset)
        if arr_len < 0 : raise ValueError("AxiomBP字节数组长度非法")
        if offset + arr_len > len(data) : raise ValueError("AxiomBP字节数组越界")
        return data[offset:offset+arr_len], offset + arr_len

    @classmethod
    def verify(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> bool :
        try :
            data = cls._read_bytes(buffer)
            if len(data) < 16 : return False

            magic, offset = cls._read_i32be(data, 0)
            if magic != cls.MAGIC : return False

            _, offset = cls._read_byte_array(data, offset)
            _, offset = cls._read_byte_array(data, offset)
            block_len, offset = cls._read_i32be(data, offset)
            if block_len < 0 : return False
            if offset + block_len != len(data) : return False

            block_data = data[offset:offset+block_len]
            if len(block_data) == 0 : return False
            root_nbt = nbt.read_from_nbt_file(io.BytesIO(gzip.decompress(block_data)), byteorder="big").get_tag()
            return isinstance(root_nbt, nbt.TAG_Compound) and isinstance(root_nbt.get("BlockRegion", None), nbt.TAG_List)
        except : return False

    @classmethod
    def _tag_to_value(cls, tag_obj):
        if isinstance(tag_obj, nbt.TAG_Byte) : return bool(tag_obj.get_value())
        if isinstance(tag_obj, (nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : return tag_obj.get_value()
        if isinstance(tag_obj, (nbt.TAG_Float, nbt.TAG_Double)) : return tag_obj.get_value()
        if isinstance(tag_obj, nbt.TAG_String) : return tag_obj.get_value()
        if isinstance(tag_obj, nbt.TAG_ByteArray) : return bytes((v & 0xff) for v in tag_obj.get_value())
        if isinstance(tag_obj, nbt.TAG_IntArray) : return [int(v) for v in tag_obj.get_value()]
        if isinstance(tag_obj, nbt.TAG_LongArray) : return [int(v) for v in tag_obj.get_value()]
        if isinstance(tag_obj, nbt.TAG_List) : return [cls._tag_to_value(i) for i in tag_obj]
        if isinstance(tag_obj, nbt.TAG_Compound) : return {k: cls._tag_to_value(v) for k, v in tag_obj.items()}
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
    def _bits_per_block(cls, palette_size:int) -> int :
        bits = 4
        while (1 << bits) < max(1, palette_size) : bits += 1
        return max(4, bits)

    @classmethod
    def _pack_block_indices(cls, indices:List[int], palette_size:int) -> List[int] :
        if palette_size <= 0 : raise ValueError("调色盘为空")
        bits = cls._bits_per_block(palette_size)
        values_per_long = max(1, 64 // bits)
        long_count = (len(indices) + values_per_long - 1) // values_per_long
        packed = [0] * long_count
        mask = (1 << bits) - 1
        for i, palette_idx in enumerate(indices) :
            if palette_idx < 0 : palette_idx = 0
            long_idx = i // values_per_long
            bit_idx = (i % values_per_long) * bits
            packed[long_idx] |= (int(palette_idx) & mask) << bit_idx

        out = []
        for value in packed :
            if value >= (1 << 63) : value -= (1 << 64)
            out.append(value)
        return out

    @classmethod
    def _unpack_block_indices(cls, data_longs:List[int], palette_size:int, total:int=4096) -> List[int] :
        if palette_size <= 0 : return [0] * total
        bits = cls._bits_per_block(palette_size)
        values_per_long = max(1, 64 // bits)
        mask = (1 << bits) - 1

        values = [0] * total
        for i in range(total) :
            long_idx = i // values_per_long
            bit_idx = (i % values_per_long) * bits
            if long_idx >= len(data_longs) :
                continue
            val = data_longs[long_idx]
            if val < 0 : val += (1 << 64)
            values[i] = (val >> bit_idx) & mask
        return values

    @classmethod
    def _to_root_compound(cls, data:bytes) -> nbt.TAG_Compound :
        root = nbt.read_from_nbt_file(io.BytesIO(data), byteorder="big").get_tag()
        if not isinstance(root, nbt.TAG_Compound) :
            raise ValueError("NBT 根标签不是 TAG_Compound")
        return root

    @classmethod
    def _is_air_name(cls, name:str) -> bool :
        return name.lower() in cls.AIR_NAME_SET

    @classmethod
    def from_buffer(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        file_bytes = cls._read_bytes(buffer)
        if not cls.verify(file_bytes) : raise ValueError("不是合法的AxiomBP文件")

        offset = 0
        _, offset = cls._read_i32be(file_bytes, offset)
        _, offset = cls._read_byte_array(file_bytes, offset)
        _, offset = cls._read_byte_array(file_bytes, offset)
        block_len, offset = cls._read_i32be(file_bytes, offset)
        block_gzip = file_bytes[offset:offset+block_len]

        block_nbt = cls._to_root_compound(gzip.decompress(block_gzip))
        regions = block_nbt.get("BlockRegion", None)
        if not isinstance(regions, nbt.TAG_List) or len(regions) == 0 :
            raise ValueError("AxiomBP缺少BlockRegion")

        min_rx, min_ry, min_rz = 2**31-1, 2**31-1, 2**31-1
        max_rx, max_ry, max_rz = -2**31, -2**31, -2**31
        for region in regions :
            if not isinstance(region, nbt.TAG_Compound) : continue
            if not ("X" in region and "Y" in region and "Z" in region) : continue
            if not isinstance(region["X"], nbt.TAG_Int) : continue
            if not isinstance(region["Y"], nbt.TAG_Int) : continue
            if not isinstance(region["Z"], nbt.TAG_Int) : continue
            rx, ry, rz = region["X"].get_value(), region["Y"].get_value(), region["Z"].get_value()
            min_rx, min_ry, min_rz = min(min_rx, rx), min(min_ry, ry), min(min_rz, rz)
            max_rx, max_ry, max_rz = max(max_rx, rx), max(max_ry, ry), max(max_rz, rz)

        if min_rx > max_rx or min_ry > max_ry or min_rz > max_rz :
            raise ValueError("AxiomBP区域坐标无效")

        size_x = (max_rx - min_rx + 1) * 16
        size_y = (max_ry - min_ry + 1) * 16
        size_z = (max_rz - min_rz + 1) * 16

        obj = cls()
        obj.size = array.array("i", [size_x, size_y, size_z])
        obj.origin = array.array("i", [min_rx * 16, min_ry * 16, min_rz * 16])
        obj.block_index = array.array("i", [0] * (size_x * size_y * size_z))

        palette_map:Dict[Tuple[str, Tuple[Tuple[str, str], ...]], int] = {}
        obj.block_palette.append({"Name":"minecraft:air", "Properties":{}})
        palette_map[("minecraft:air", tuple())] = 0

        for region in regions :
            if not isinstance(region, nbt.TAG_Compound) : continue
            if not ("X" in region and "Y" in region and "Z" in region and "BlockStates" in region) : continue
            if not isinstance(region["X"], nbt.TAG_Int) : continue
            if not isinstance(region["Y"], nbt.TAG_Int) : continue
            if not isinstance(region["Z"], nbt.TAG_Int) : continue
            if not isinstance(region["BlockStates"], nbt.TAG_Compound) : continue

            rx, ry, rz = region["X"].get_value(), region["Y"].get_value(), region["Z"].get_value()
            bs = region["BlockStates"]
            if not ("palette" in bs and "data" in bs) : continue
            if not isinstance(bs["palette"], nbt.TAG_List) : continue
            if not isinstance(bs["data"], nbt.TAG_LongArray) : continue

            region_palette:List[int] = []
            for pal in bs["palette"] :
                if not isinstance(pal, nbt.TAG_Compound) :
                    region_palette.append(0)
                    continue

                name = "minecraft:air"
                props:Dict[str, str] = {}
                if "Name" in pal and isinstance(pal["Name"], nbt.TAG_String) :
                    name = pal["Name"].get_value().strip() or "minecraft:air"
                if not ":" in name : name = "minecraft:" + name

                if cls._is_air_name(name) :
                    region_palette.append(0)
                    continue

                if "Properties" in pal and isinstance(pal["Properties"], nbt.TAG_Compound) :
                    for key, val in pal["Properties"].items() :
                        if isinstance(val, nbt.TAG_String) : props[key] = val.get_value()
                        elif isinstance(val, (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long, nbt.TAG_Float, nbt.TAG_Double)) :
                            props[key] = str(val.get_value()).lower()

                cache_key = (name, tuple(sorted((k, str(v)) for k, v in props.items())))
                if cache_key in palette_map :
                    region_palette.append(palette_map[cache_key])
                else :
                    idx = len(obj.block_palette)
                    palette_map[cache_key] = idx
                    obj.block_palette.append({"Name": name, "Properties": props})
                    region_palette.append(idx)

            block_vals = cls._unpack_block_indices([int(v) for v in bs["data"].get_value()], len(region_palette), total=4096)
            base_x = (rx - min_rx) * 16
            base_y = (ry - min_ry) * 16
            base_z = (rz - min_rz) * 16

            for block_idx in range(4096) :
                local_y = block_idx // 256
                rem = block_idx % 256
                local_z = rem // 16
                local_x = rem % 16

                gx, gy, gz = base_x + local_x, base_y + local_y, base_z + local_z
                if not (0 <= gx < size_x and 0 <= gy < size_y and 0 <= gz < size_z) : continue

                p = block_vals[block_idx]
                if p < 0 or p >= len(region_palette) : p = 0
                index = (gx * size_y + gy) * size_z + gz
                obj.block_index[index] = region_palette[p]

        if "BlockEntities" in block_nbt and isinstance(block_nbt["BlockEntities"], nbt.TAG_List) :
            size_y, size_z = obj.size[1], obj.size[2]
            for block_entity in block_nbt["BlockEntities"] :
                if not isinstance(block_entity, nbt.TAG_Compound) : continue
                if not ("x" in block_entity and "y" in block_entity and "z" in block_entity) : continue
                if not isinstance(block_entity["x"], (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : continue
                if not isinstance(block_entity["y"], (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : continue
                if not isinstance(block_entity["z"], (nbt.TAG_Byte, nbt.TAG_Short, nbt.TAG_Int, nbt.TAG_Long)) : continue

                gx = block_entity["x"].get_value() - obj.origin[0]
                gy = block_entity["y"].get_value() - obj.origin[1]
                gz = block_entity["z"].get_value() - obj.origin[2]
                if not (0 <= gx < obj.size[0] and 0 <= gy < obj.size[1] and 0 <= gz < obj.size[2]) : continue

                index = (gx * size_y + gy) * size_z + gz
                obj.block_nbt[index] = block_entity.copy()

        if "Entities" in block_nbt and isinstance(block_nbt["Entities"], nbt.TAG_List) :
            for entity in block_nbt["Entities"] :
                if isinstance(entity, nbt.TAG_Compound) : obj.entity_nbt.append(entity.copy())

        return obj

    @classmethod
    def _floor_div(cls, a:int, b:int) -> int :
        return a // b if a >= 0 else -((-a + b - 1) // b)

    @classmethod
    def _mod(cls, a:int, b:int) -> int :
        return a % b if a >= 0 else (b - ((-a) % b)) % b

    def _build_metadata(self, target_name:str, block_count:int, contains_air:bool) -> bytes :
        struct_name = os.path.basename(target_name) if target_name else "AxiomStructure"
        if "." in struct_name : struct_name = ".".join(struct_name.split(".")[:-1])
        if not struct_name.strip() : struct_name = "AxiomStructure"

        author = os.environ.get("USER", "") or os.environ.get("USERNAME", "") or "Command_Simulator"

        meta = nbt.TAG_Compound()
        meta["ThumbnailYaw"] = nbt.TAG_Float(0)
        meta["ContainsAir"] = nbt.TAG_Byte(1 if contains_air else 0)
        meta["Version"] = nbt.TAG_Int(2)
        meta["LockedThumbnail"] = nbt.TAG_Byte(0)
        meta["BlockCount"] = nbt.TAG_Int(block_count)
        meta["Author"] = nbt.TAG_String(author)
        meta["Tags"] = nbt.TAG_List(type=nbt.TAG_String)
        meta["Name"] = nbt.TAG_String(struct_name)
        meta["ThumbnailPitch"] = nbt.TAG_Float(0)
        return self._nbt_to_bytes(meta, byteorder="big")

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        size_x, size_y, size_z = [int(v) for v in self.size]
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("size 不是合法结构尺寸")

        volume = size_x * size_y * size_z
        if len(self.block_index) != volume :
            raise ValueError("block_index 长度与结构体积不一致")

        if len(self.block_palette) == 0 :
            self.block_palette.append({"Name":"minecraft:air", "Properties":{}})

        for i, idx in enumerate(self.block_index) :
            if not (0 <= idx < len(self.block_palette)) : self.block_index[i] = 0

        start_x, start_y, start_z = [int(v) for v in self.origin]
        end_x, end_y, end_z = start_x + size_x - 1, start_y + size_y - 1, start_z + size_z - 1

        start_rx, start_ry, start_rz = self._floor_div(start_x, 16), self._floor_div(start_y, 16), self._floor_div(start_z, 16)
        end_rx, end_ry, end_rz = self._floor_div(end_x, 16), self._floor_div(end_y, 16), self._floor_div(end_z, 16)

        root = nbt.TAG_Compound()
        root["DataVersion"] = nbt.TAG_Int(self.JAVA_DATA_VERSION)
        root["BlockRegion"] = nbt.TAG_List(type=nbt.TAG_Compound)
        root["BlockEntities"] = nbt.TAG_List(type=nbt.TAG_Compound)
        root["Entities"] = nbt.TAG_List(type=nbt.TAG_Compound)

        non_air = 0
        for ry in range(start_ry, end_ry + 1) :
            for rz in range(start_rz, end_rz + 1) :
                for rx in range(start_rx, end_rx + 1) :
                    local_indices = [0] * 4096
                    region_palette:List[Dict[str, dict]] = []
                    palette_map:Dict[int, int] = {}

                    def add_region_palette(global_idx:int) -> int :
                        if global_idx in palette_map : return palette_map[global_idx]
                        palette_map[global_idx] = len(region_palette)
                        palette_data = self.block_palette[global_idx]
                        region_palette.append({
                            "Name": str(palette_data.get("Name", "minecraft:air")),
                            "Properties": dict(palette_data.get("Properties", {}) if isinstance(palette_data.get("Properties", {}), dict) else {})
                        })
                        return palette_map[global_idx]

                    add_region_palette(0)
                    region_world_x, region_world_y, region_world_z = rx * 16, ry * 16, rz * 16
                    for ly in range(16) :
                        world_y = region_world_y + ly
                        for lz in range(16) :
                            world_z = region_world_z + lz
                            for lx in range(16) :
                                world_x = region_world_x + lx
                                block_pos_idx = ly * 256 + lz * 16 + lx

                                if not (start_x <= world_x <= end_x and start_y <= world_y <= end_y and start_z <= world_z <= end_z) :
                                    local_indices[block_pos_idx] = 0
                                    continue

                                gx, gy, gz = world_x - start_x, world_y - start_y, world_z - start_z
                                global_index = (gx * size_y + gy) * size_z + gz
                                gpal = int(self.block_index[global_index])
                                if gpal != 0 : non_air += 1
                                local_indices[block_pos_idx] = add_region_palette(gpal)

                    packed = self._pack_block_indices(local_indices, len(region_palette))
                    palette_tag = nbt.TAG_List(type=nbt.TAG_Compound)
                    for pal in region_palette :
                        entry = nbt.TAG_Compound()
                        entry["Name"] = nbt.TAG_String(pal["Name"] if ":" in pal["Name"] else "minecraft:" + pal["Name"])

                        props = pal.get("Properties", {})
                        if isinstance(props, dict) and len(props) > 0 :
                            props_tag = nbt.TAG_Compound()
                            for k, v in props.items() :
                                if not isinstance(k, str) : continue
                                if isinstance(v, bool) : props_tag[k] = nbt.TAG_String("true" if v else "false")
                                else : props_tag[k] = nbt.TAG_String(str(v).lower() if isinstance(v, (int, float)) else str(v))
                            if len(props_tag) : entry["Properties"] = props_tag
                        palette_tag.append(entry)

                    bs = nbt.TAG_Compound()
                    bs["palette"] = palette_tag
                    bs["data"] = nbt.TAG_LongArray(array.array("q", packed))

                    region = nbt.TAG_Compound()
                    region["BlockStates"] = bs
                    region["X"] = nbt.TAG_Int(rx)
                    region["Y"] = nbt.TAG_Int(ry)
                    region["Z"] = nbt.TAG_Int(rz)
                    root["BlockRegion"].append(region)

        for index, be in self.block_nbt.items() :
            if not isinstance(index, int) : continue
            if not isinstance(be, nbt.TAG_Compound) : continue
            if not (0 <= index < len(self.block_index)) : continue

            gx = index // (size_y * size_z)
            gy = (index % (size_y * size_z)) // size_z
            gz = index % size_z
            world_x, world_y, world_z = start_x + gx, start_y + gy, start_z + gz

            be_copy = be.copy()
            be_copy["x"] = nbt.TAG_Int(world_x)
            be_copy["y"] = nbt.TAG_Int(world_y)
            be_copy["z"] = nbt.TAG_Int(world_z)
            root["BlockEntities"].append(be_copy)

        for entity in self.entity_nbt :
            if isinstance(entity, nbt.TAG_Compound) : root["Entities"].append(entity.copy())

        block_data = gzip.compress(self._nbt_to_bytes(root, byteorder="big"))
        contains_air = non_air < volume
        target_name = buffer if isinstance(buffer, str) else "AxiomStructure.bp"
        metadata = self._build_metadata(target_name, non_air, contains_air)

        output = io.BytesIO()
        output.write(struct.pack(">i", self.MAGIC))
        output.write(struct.pack(">i", len(metadata)))
        output.write(metadata)
        output.write(struct.pack(">i", 0))
        output.write(struct.pack(">i", len(block_data)))
        output.write(block_data)

        self._write_bytes(buffer, output.getvalue())

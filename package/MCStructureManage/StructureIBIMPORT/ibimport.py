import os, io, json, array
from .. import nbt
from ..__private import TypeCheckList
from typing import Union, List, Dict
from io import FileIO, BytesIO


class IBImport :
    """
    IBImport 文件对象（仅编码）
    -----------------------
    * 结构：IBImport + XOR分段（text + json占位）
    * 可用方法 save_as : 通过路径或缓冲区保存数据
    * 可用类方法 from_buffer : 不支持（仅编码）
    """

    HEADER = b"IBImport "
    SEG0_KEY = 0x16
    SEG1_KEY = 0x94

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
    def from_buffer(cls, buffer:Union[str, bytes, FileIO, BytesIO]) :
        raise RuntimeError(f"{buffer} 不支持通过 IBImport 解码为结构")

    @classmethod
    def _write_bytes(cls, buffer:Union[str, FileIO, BytesIO], data:bytes) :
        if isinstance(buffer, str) :
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            with open(buffer, "wb") as _f : _f.write(data)
            return

        if isinstance(buffer, io.IOBase) :
            if buffer.seekable() :
                buffer.seek(0)
                try : buffer.truncate(0)
                except : pass

            if isinstance(buffer, io.TextIOBase) : buffer.write(data.decode("latin1"))
            else : buffer.write(data)
            return

        raise TypeError(f"{buffer} 不是可写入对象")

    @classmethod
    def _write_varint32(cls, value:int) -> bytes :
        if value < 0 : raise ValueError("varint32 不能为负数")
        out = bytearray()
        while True :
            byte = value & 0x7f
            value >>= 7
            if value : out.append(byte | 0x80)
            else :
                out.append(byte)
                break
        return bytes(out)

    @classmethod
    def _xor_bytes(cls, data:bytes, key:int) -> bytes :
        key = key & 0xff
        return bytes((b ^ key) for b in data)

    @classmethod
    def _format_rel(cls, value:int) -> str :
        return "~" if value == 0 else f"~{value}"

    @classmethod
    def _format_state(cls, states:dict) -> str :
        if not isinstance(states, dict) or not states : return "[]"
        state_str = json.dumps(states, ensure_ascii=False, separators=(",", "="))
        return f"[{state_str[1:-1]}]"

    @classmethod
    def _strip_namespace(cls, name:str) -> str :
        if not isinstance(name, str) : return "unknown"
        name = name.strip()
        if not name : return "unknown"
        if ":" in name : return name.split(":", 1)[1]
        return name

    def _build_segment0_plain(self, ignore_air:bool=True) -> bytes :
        size_x, size_y, size_z = map(int, self.size)
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("结构尺寸无效")

        lines:List[str] = []
        volume = size_x * size_y * size_z
        for index in range(min(volume, len(self.block_index))) :
            palette_index = int(self.block_index[index])
            if not (0 <= palette_index < len(self.block_palette)) : continue

            block = self.block_palette[palette_index]
            block_name = str(block.get("name", "minecraft:air"))
            if ignore_air and block_name in ("minecraft:air", "minecraft:void_air", "minecraft:cave_air") :
                continue

            x = index // (size_y * size_z)
            y = (index % (size_y * size_z)) // size_z
            z = index % size_z

            name = self._strip_namespace(block_name)
            state = self._format_state(block.get("states", {}))
            if not state : state = "[]"
            lines.append(f"setblock {self._format_rel(x)} {self._format_rel(y)} {self._format_rel(z)} {name} {state}\n")

        lines.append("setblock ~ ~ ~ air []\n")
        if not (size_x == 1 and size_y == 1 and size_z == 1) :
            lines.append(
                "setblock %s %s %s air []\n" % (
                    self._format_rel(size_x - 1),
                    self._format_rel(size_y - 1),
                    self._format_rel(size_z - 1),
                )
            )

        return "".join(lines).encode("utf-8")

    def _build_segment(self, plain:bytes, key:int) -> bytes :
        return self._write_varint32(len(plain)) + bytes([key & 0xff]) + self._xor_bytes(plain, key)

    def save_as(self, buffer:Union[str, FileIO, BytesIO], ignore_air:bool=True) :
        seg0_plain = self._build_segment0_plain(ignore_air=ignore_air)
        seg1_plain = b"[]\n"

        out = bytearray()
        out.extend(self.HEADER)
        out.extend(self._build_segment(seg0_plain, self.SEG0_KEY))
        out.extend(self._build_segment(seg1_plain, self.SEG1_KEY))
        self._write_bytes(buffer, bytes(out))

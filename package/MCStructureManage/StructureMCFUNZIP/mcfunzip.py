import os, io, gzip, json, array
from .. import nbt
from ..__private import TypeCheckList
from typing import Union, List, Dict
from io import FileIO, BytesIO

try :
    from ...Py_module import msgpack
except Exception :
    import msgpack


class MCFunZip :
    """
    MCFunZip 文件对象（仅编码）
    -----------------------
    * 结构：mczip@ + gzip(msgpack([cmd_list, block_list, param_list]))
    * 可用方法 save_as : 通过路径或缓冲区保存数据
    * 可用类方法 from_buffer : 不支持（仅编码）
    """

    HEADER = b"mczip@"

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
        raise RuntimeError(f"{buffer} 不支持通过 MCFunZip 解码为结构")

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
    def _format_rel(cls, value:int) -> str :
        return "~" if value == 0 else f"~{value}"

    @classmethod
    def _format_state(cls, states:dict) -> str :
        if not isinstance(states, dict) or not states : return "[]"
        state_str = json.dumps(states, ensure_ascii=False, separators=(",", "="))
        return f"[{state_str[1:-1]}]"

    @classmethod
    def _block_token(cls, block:dict) -> str :
        name = str(block.get("name", "minecraft:air"))
        state = cls._format_state(block.get("states", {}))
        if state == "[]" : token = name
        else : token = f"{name}{state}"

        if ":" in token : token = token.split(":", 1)[1]
        return token.strip()

    def save_as(self, buffer:Union[str, FileIO, BytesIO], ignore_air:bool=True) :
        size_x, size_y, size_z = map(int, self.size)
        if size_x <= 0 or size_y <= 0 or size_z <= 0 :
            raise ValueError("结构尺寸无效")

        blocks_index = {}
        all_blocks:List[str] = []
        param_data_list:List[list] = []
        volume = size_x * size_y * size_z

        for index in range(min(volume, len(self.block_index))) :
            palette_index = int(self.block_index[index])
            if not (0 <= palette_index < len(self.block_palette)) : continue
            block = self.block_palette[palette_index]

            block_name = str(block.get("name", "minecraft:air"))
            if ignore_air and block_name in ("minecraft:air", "minecraft:void_air", "minecraft:cave_air") :
                continue

            block_id = self._block_token(block)
            if not block_id : continue

            if block_id not in blocks_index :
                blocks_index[block_id] = len(all_blocks)
                all_blocks.append(block_id)
            bi = blocks_index[block_id]

            x = index // (size_y * size_z)
            y = (index % (size_y * size_z)) // size_z
            z = index % size_z

            param_data_list.append([
                1, 0,
                1, bi,
                0, self._format_rel(x), self._format_rel(y), self._format_rel(z), 0,
            ])

        packed = msgpack.packb([
            ["setblock"],
            all_blocks,
            param_data_list,
        ], use_bin_type=True)

        out = self.HEADER + gzip.compress(packed)
        self._write_bytes(buffer, out)

import os, io, array, struct, hashlib, hmac
from .. import nbt, StructureMCS
from ..__private import TypeCheckList
from typing import Union, List, Dict
from io import FileIO, BytesIO


class Nexus :
    """
    Nexus 结构文件对象
    -----------------------
    * 管理 .nexus 为后缀的二进制结构文件
    * 实际内容是 mcstructure 的可选Brotli压缩封装
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构原点坐标
    * 可用属性 block_index : 方块索引列表
    * 可用属性 block_palette : 调色盘对象列表
    * 可用属性 block_nbt : 方块NBT字典
    * 可用属性 entity_nbt : 实体NBT列表
    * 可用属性 author : 作者信息
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数组或缓冲区生成对象
    * 可用方法 save_as : 通过路径或缓冲区保存对象数据
    """

    MAGIC = b"NXUS"
    VERSION = 1
    COMP_NONE = 0
    COMP_BROTLI = 1
    FLAG_AUTHOR = 1 << 0
    FLAG_PASSWORD = 1 << 1

    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.origin: array.array = array.array("i", [0, 0, 0])
        self.block_index: array.array = array.array("i")
        self.block_palette: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.author:str = ""

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


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
    def _read_exact(cls, reader:io.IOBase, size:int, error_text:str) -> bytes :
        data = reader.read(size)
        if not isinstance(data, (bytes, bytearray)) or len(data) != size :
            raise ValueError(error_text)
        return bytes(data)

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
    def _nbt_to_bytes(cls, tag:nbt.TAG_Compound, byteorder: str = "little") -> bytes :
        mem = io.BytesIO()
        nbt.write_to_nbt_file(mem, tag, zip_mode="none", byteorder=byteorder)
        return mem.getvalue()

    @classmethod
    def _brotli_decompress(cls, data:bytes) -> bytes :
        try :
            from .. import brotli
            return brotli.decompress(data)
        except :
            import brotli
            return brotli.decompress(data)

    @classmethod
    def _brotli_compress(cls, data:bytes) -> bytes :
        try :
            from .. import brotli
            return brotli.compress(data)
        except :
            import brotli
            return brotli.compress(data)

    @classmethod
    def verify(cls, buffer:Union[str, bytes, FileIO, BytesIO]) -> bool :
        reader, need_close = None, False
        try :
            reader, need_close = cls._open_reader(buffer)
            head = cls._read_exact(reader, 8, "Nexus文件长度无效")
            if head[:4] != cls.MAGIC : return False
            if head[4] != cls.VERSION : return False
            return True
        except : return False
        finally :
            if need_close and reader is not None :
                try : reader.close()
                except : pass

    @classmethod
    def from_buffer(cls, buffer:Union[str, bytes, FileIO, BytesIO], password:str="") :
        reader, need_close = cls._open_reader(buffer)
        try :
            head = cls._read_exact(reader, 8, "Nexus文件长度无效")
            if head[:4] != cls.MAGIC : raise ValueError("不是Nexus文件")

            version, flags, compression = head[4], head[5], head[6]
            if version != cls.VERSION : raise ValueError("Nexus版本不受支持")

            author = ""
            if flags & cls.FLAG_AUTHOR :
                author_len = struct.unpack("<H", cls._read_exact(reader, 2, "Nexus作者字段损坏"))[0]
                author = cls._read_exact(reader, author_len, "Nexus作者字段损坏").decode("utf-8", "replace")

            if flags & cls.FLAG_PASSWORD :
                password_blob = cls._read_exact(reader, 48, "Nexus密码字段损坏")
                salt = password_blob[:16]
                digest = password_blob[16:48]

                if not password : raise ValueError("该Nexus文件需要密码")
                calc = hashlib.sha256(salt + password.encode("utf-8")).digest()
                if not hmac.compare_digest(calc, digest) : raise ValueError("Nexus密码错误")

            payload = reader.read()
        finally :
            if need_close :
                try : reader.close()
                except : pass

        if compression == cls.COMP_NONE :
            pass
        elif compression == cls.COMP_BROTLI :
            payload = cls._brotli_decompress(payload)
        else :
            raise ValueError("Nexus压缩方式不受支持")

        mcs = StructureMCS.Mcstructure.from_buffer(io.BytesIO(payload))
        ret = cls()
        ret.size = array.array("i", mcs.size)
        ret.origin = array.array("i", mcs.origin)
        ret.block_index = array.array("i", mcs.block_index)
        ret.block_palette = TypeCheckList(i.copy() for i in mcs.block_palette).setChecker(nbt.TAG_Compound)
        ret.block_nbt = {k:v.copy() for k,v in mcs.block_nbt.items()}
        ret.entity_nbt = TypeCheckList(i.copy() for i in mcs.entity_nbt).setChecker(nbt.TAG_Compound)
        ret.author = author
        return ret

    def save_as(self, buffer:Union[str, FileIO, BytesIO], password:str="", author:str="", compression:int=1) :
        mcs = StructureMCS.Mcstructure()
        mcs.size = array.array("i", self.size)
        mcs.origin = array.array("i", self.origin)
        mcs.block_index = array.array("i", self.block_index)
        mcs.contain_index = array.array("i", b"\xff\xff\xff\xff" * len(self.block_index))
        mcs.block_palette = TypeCheckList(i.copy() for i in self.block_palette).setChecker(nbt.TAG_Compound)
        mcs.entity_nbt = TypeCheckList(i.copy() for i in self.entity_nbt).setChecker(nbt.TAG_Compound)
        mcs.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}

        mem = io.BytesIO()
        mcs.save_as(mem)
        payload = mem.getvalue()

        if compression == self.COMP_BROTLI : payload = self._brotli_compress(payload)
        elif compression != self.COMP_NONE : raise ValueError("不支持的Nexus压缩方式")

        out = bytearray()
        out.extend(self.MAGIC)

        flags = 0
        author_use = author if isinstance(author, str) else ""
        if author_use : flags |= self.FLAG_AUTHOR
        if isinstance(password, str) and password : flags |= self.FLAG_PASSWORD

        out.extend(bytes([self.VERSION, flags, compression, 0]))

        if flags & self.FLAG_AUTHOR :
            author_bytes = author_use.encode("utf-8")
            if len(author_bytes) > 0xffff : raise ValueError("author长度超过65535")
            out.extend(struct.pack("<H", len(author_bytes)))
            out.extend(author_bytes)

        if flags & self.FLAG_PASSWORD :
            salt = os.urandom(16)
            digest = hashlib.sha256(salt + password.encode("utf-8")).digest()
            out.extend(salt)
            out.extend(digest)

        out.extend(payload)
        self._write_bytes(buffer, bytes(out))

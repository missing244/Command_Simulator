import struct, zlib, math
from io import IOBase, BytesIO
from typing import Tuple, Union

class SimplePNG:
    """简单的PNG对象，支持生成和缩放"""

    def __init__(self, width:int, height:int):
        self.__width = math.floor(width)
        self.__height = math.floor(height)
        self.__pixels = bytearray((width*4 + 1)*height)
    
    @property
    def memory_view(self) :
        return memoryview(self.__pixels)

    @property
    def width(self) :
        return self.__width

    @property
    def height(self) :
        return self.__height

    @property
    def size(self) :
        return (self.width, self.height)


    def get_pixel(self, x:int, y:int) -> Tuple[int, int, int, float] :
        index = y * (1 + self.__width * 4) + 1 + x * 4
        poixel = self.__pixels[index:index+4]
        return (poixel[0], poixel[1], poixel[2], poixel[3]/255)

    def set_pixel(self, x:int, y:int, rgba:Tuple[int, int, int, float]) :
        index = y * (1 + self.__width * 4) + 1 + x * 4
        pixels = self.__pixels
        pixels[index] = rgba[0]
        pixels[index+1] = rgba[1]
        pixels[index+2] = rgba[2]
        pixels[index+3] = int(rgba[3]*255)

    def resize(self, width:int, height:int) -> "SimplePNG" :
        """最近邻缩放"""
        src_height = self.height
        src_width = self.width
        dst_width, dst_height = width, height
        result = self.__class__(dst_width, dst_height)
        
        for dst_y in range(dst_height):
            src_y = int(dst_y * src_height / dst_height)
            src_y = min(src_y, src_height - 1)
            for dst_x in range(dst_width):
                src_x = int(dst_x * src_width / dst_width)
                src_x = min(src_x, src_width - 1)
                result.set_pixel( dst_x, dst_y, self.get_pixel(src_x, src_y) )
        return result


    def save_as(self, buffer:Union[str, IOBase, BytesIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "wb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        
        compressed = zlib.compress(self.__pixels)

        #PNG Header
        _file.write(b'\x89PNG\r\n\x1a\n')
        # IHDR
        ihdr = struct.pack('>IIBBBBB', self.width, self.height, 8, 6, 0, 0, 0)
        _file.write(struct.pack('>I', 13))
        _file.write(b'IHDR')
        _file.write(ihdr)
        _file.write(struct.pack('>I', zlib.crc32(b'IHDR' + ihdr) & 0xffffffff))
        # IDAT
        _file.write(struct.pack('>I', len(compressed)))
        _file.write(b'IDAT')
        _file.write(compressed)
        _file.write(struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff))
        # IEND
        _file.write(struct.pack('>I', 0))
        _file.write(b'IEND')
        _file.write(struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff))

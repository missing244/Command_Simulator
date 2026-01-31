r"""
    __init__.py - 关于 Minecraft - NBT 的 Python 库

                       _ooOoo_
                      o8888888o
                      88" . "88
                      (| -_- |)
                      O\  =  /O
                   ____/`---'\____
                 .'  \|     |//  `.
                /  \|||  :  |||//  \
               /  _||||| -:- |||||-  \
               |   | \\  -  /// |   |
               | \_|  ''\---/''  |   |
               \  .-\__  `-`  ___/-. /
             ___`. .'  /--.--\  `. . __
          ."" '<  `.___\_<|>_/___.'  >'"".
         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
         \  \ `-.   \_ __\ /__ _/   .-` /  /
    ======`-.____`-.___\_____\/___.-`____.-'======
                       `=---='
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                佛祖保佑       永无BUG
"""

class TAG(__import__('enum').Enum):
    END        = 0
    BYTE       = 1
    SHORT      = 2
    INT        = 3
    LONG       = 4
    FLOAT      = 5
    DOUBLE     = 6
    BYTE_ARRAY = 7
    STRING     = 8
    LIST       = 9
    COMPOUND   = 10
    INT_ARRAY  = 11
    LONG_ARRAY = 12

TAGLIST = {}

from .error import (
    SnbtParseError,
    SnbtTokenError,
    NbtParseError,
    NbtFileError,
    NbtBufferError,
    NbtContextError,
    NbtDataError,
)
from .tags import (
    TAG_End,
    TAG_Byte,
    TAG_Short,
    TAG_Int,
    TAG_Long,
    TAG_Float,
    TAG_Double,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_ByteArray,
    TAG_IntArray,
    TAG_LongArray,
)
from .root import (
    read_from_nbt_file,
    read_from_dat_file,
    read_from_snbt_file,
    write_to_nbt_file,
    write_to_dat_file,
    write_to_snbt_file,
    RootNBT,
)

from .builder import (
    NBT_Builder
)

TAGLIST[TAG.END]        = TAG_End
TAGLIST[TAG.BYTE]       = TAG_Byte
TAGLIST[TAG.SHORT]      = TAG_Short
TAGLIST[TAG.INT]        = TAG_Int
TAGLIST[TAG.LONG]       = TAG_Long
TAGLIST[TAG.FLOAT]      = TAG_Float
TAGLIST[TAG.DOUBLE]     = TAG_Double
TAGLIST[TAG.STRING]     = TAG_String
TAGLIST[TAG.LIST]       = TAG_List
TAGLIST[TAG.COMPOUND]   = TAG_Compound
TAGLIST[TAG.BYTE_ARRAY] = TAG_ByteArray
TAGLIST[TAG.INT_ARRAY]  = TAG_IntArray
TAGLIST[TAG.LONG_ARRAY] = TAG_LongArray

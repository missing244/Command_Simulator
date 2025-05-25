import os
from typing import Literal,Union,List,Tuple

Encrypt_Header = b"\x80\x1d\x30\x01"



def GetWorldEdtion(path:str) :
    """
    获取文件路径对应的存档类型
    * 返回 Netease 字符串: 世界是网易版世界
    * 返回 Bedrock 字符串: 世界是基岩版世界
    * 返回 None : 此存档并不是世界存档
    """
    if not os.path.isfile(os.path.join(path, "level.dat")) : return None
    if not os.path.isfile(os.path.join(path, "db", "CURRENT")) : return None

    with open(os.path.join(path, "db", "CURRENT"), "rb") as _file :
        byte1 = _file.read(4)
        if byte1 == Encrypt_Header : return "Netease"
        else : return "Bedrock"

def GetWorldEncryptKey(path:str) :
    """
    获取文件路径对应的存档加密密钥
    * 返回 int : 此存档的数字密钥
    * 返回 None : 此存档并不是加密存档
    """
    db_file_path = os.path.join(path, "db", "CURRENT")
    if not os.path.isfile(db_file_path) : return None
    with open(db_file_path, "rb") as CURRENT :
        KeyBytes = CURRENT.read(12)
        if KeyBytes[0:4] != Encrypt_Header : return None
        SECRET_KEY = bytes( (i^j for i,j in zip(b"MANIFEST", KeyBytes[4:])) )
        return int.from_bytes(SECRET_KEY, byteorder="big")



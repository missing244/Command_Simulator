from . import nbt
from typing import Union,Dict,Tuple
import json, random, os

CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
Translate = json.load(fp=open(os.path.join(CurrentPath, "res", "translate.json"), "r", encoding="utf-8"))
EntityNBT:Dict[str, nbt.TAG_Compound] = {}
def InitEntityNBT() :
    import gzip
    NBTGzipFile = gzip.GzipFile(os.path.join(CurrentPath, "res", "entityNBT.gzip"), "rb")
    while 1 :
        byte_len1 = NBTGzipFile.read(4)
        byte_len2 = NBTGzipFile.read(4)
        if (not byte_len1) or (not byte_len2) : break

        byte_len1 = int.from_bytes(byte_len1, "big")
        byte_len2 = int.from_bytes(byte_len2, "big")
        byte_data1 = NBTGzipFile.read(byte_len1)
        byte_data2 = NBTGzipFile.read(byte_len2)
        if (not byte_data1) or (not byte_data2) : break

        EntityNBT[byte_data1.decode("utf-8")] = nbt.read_from_nbt_file(byte_data2).get_tag()
InitEntityNBT()




def GenerateEntity(id:str, pos:Tuple[int, int, int], name:str=None) -> Union[nbt.TAG_Compound, None] :
    id = id if id.startswith("minecraft:") else f"minecraft:{id}"
    if id not in EntityNBT : return None
  
    NBTdata = EntityNBT[id].copy()
    NBTdata["UniqueID"] = nbt.TAG_Long(random.randint(-2**63, -2**61))
    for i in range(3) : NBTdata["Pos"][i] = nbt.TAG_Float(pos[i])
    if isinstance(name, str) : NBTdata["CustomName"] = nbt.TAG_String(name)

    return NBTdata


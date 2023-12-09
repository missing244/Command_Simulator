from typing import List,Dict,Union,Literal
from . import np
import base64,zlib


def read_json(json:dict, key_list:List[str]) :
    for key1 in key_list : 
        if key1 not in json : return None
        json = json[key1]
    return json

def encoding(obj):
    from .nbt_class import BaseNbtClass as nbt_class
    if isinstance(obj, bool): return {"value":bool(obj),"__type__":"Bool"}
    elif isinstance(obj, np.int8): return {"value":int(obj),"__type__":"Byte"}
    elif isinstance(obj, np.int16): return {"value":int(obj),"__type__":"Short"}
    elif isinstance(obj, np.int32): return {"value":int(obj),"__type__":"Int"}
    elif isinstance(obj, np.int64): return {"value":int(obj),"__type__":"Long"}
    elif isinstance(obj, np.float32): return {"value":float(np.float32(obj)),"__type__":"Float"}
    elif isinstance(obj, np.float64): return {"value":float(np.float64(obj)),"__type__":"Double"}
    elif isinstance(obj, nbt_class.entity_nbt): return obj.__save__()
    elif isinstance(obj, nbt_class.block_nbt): return obj.__save__()
    elif isinstance(obj, nbt_class.item_nbt): return obj.__save__()
    elif isinstance(obj, nbt_class.structure_nbt): return obj.__save__()
    elif isinstance(obj, nbt_class.scoreboard_nbt): return obj.__save__()
    elif isinstance(obj, nbt_class.chunk_nbt): return obj.__save__()
    elif isinstance(obj, nbt_class.world_nbt): return obj.__save__()
    else : raise TypeError("Object of type %s is not JSON serializable" %(obj.__class__.__name__,))

def decoding(obj:dict):
    from .nbt_class import BaseNbtClass as nbt_class
    test1 = ('value' in obj) and ('__type__' in obj)
    test2 = ('__minecraft_type__' in obj)

    if test2 and obj['__minecraft_type__'] == "entity_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.entity_nbt().__load__(obj)
    elif test2 and obj['__minecraft_type__'] == "block_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.block_nbt().__load__(obj)
    elif test2 and obj['__minecraft_type__'] == "item_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.item_nbt().__load__(obj)
    elif test2 and obj['__minecraft_type__'] == "structure_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.structure_nbt().__load__(obj)
    elif test2 and obj['__minecraft_type__'] == "scoreboard_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.scoreboard_nbt().__load__(obj)
    elif test2 and obj['__minecraft_type__'] == "chunk_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.chunk_nbt().__load__(obj)
    elif test2 and obj['__minecraft_type__'] == "world_nbt" :
        del obj['__minecraft_type__']
        return nbt_class.world_nbt().__load__(obj)
    elif test1 and obj['__type__'] == "Bool": return bool(obj['value'])
    elif test1 and obj['__type__'] == "Byte": return np.int8(obj['value'])
    elif test1 and obj['__type__'] == "Short": return np.int16(obj['value'])
    elif test1 and obj['__type__'] == "Int": return np.int32(obj['value'])
    elif test1 and obj['__type__'] == "Long": return np.int64(obj['value'])
    elif test1 and obj['__type__'] == "Float":  return np.float32(obj['value'])
    elif test1 and obj['__type__'] == "Double": return np.float64(obj['value'])
    else : return obj

def zip_to_string(base64code:str) : 
    return zlib.decompress(base64.b64decode(base64code.encode('utf-8'))).decode('utf-8')

def string_to_zip(str1:str) : 
    return base64.b64encode(zlib.compress(str1.encode('utf-8'))).decode('utf-8')
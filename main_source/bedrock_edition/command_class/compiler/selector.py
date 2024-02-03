from typing import Dict,Union,List,Tuple,Literal
from ... import RunTime,BaseNbtClass,MathFunction,np,Constants
from .. import COMMAND_CONTEXT,COMMAND_TOKEN,Response
from . import CompileError
import re,functools,math,random,itertools,math

DIMENSION_LIST= list(Constants.DIMENSION_INFO)
DISTANCE_FUNC = lambda item,origin_x,origin_y,origin_z : ((item.Pos[0]-origin_x)**2 + (item.Pos[1]-origin_y)**2 + (item.Pos[2]-origin_z)**2) ** 0.5

SELECTOR_VAR_MEMEROY:Dict[int,dict] = {0:{"sort":"nearest"}}


def minecraft_ID_transfor(s:str) :
    if ":" not in s : return "minecraft:%s" % s
    return s

def Quotation_String_transfor_2(s:str) -> str :
    """将字符直接拿去双引号"""
    if s[0] != "\"" or s[-1] != "\"" : return s
    return s[1:len(s)-1]



class tools :
    def scores_test(game_tread:RunTime.minecraft_thread, board_test:str, 
                    entity:Union[BaseNbtClass.entity_nbt,str], mode:Literal["if","unless"]) :
        board_name, var1, var2 = board_test["board"], board_test["min"], board_test["max"]
        a = game_tread.minecraft_scoreboard.____get_score____(board_name, entity)
        if a == Exception : return False
        elif mode == "if" : return var1 <= a <= var2
        elif mode == "unless" : return not(var1 <= a <= var2)

def Selector_Var_Condition_Test(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, origin:Tuple[int,int,int],
    selector_var:dict, entity:BaseNbtClass.entity_nbt, is_alive:bool=True) -> bool :
    if is_alive and hasattr(entity,"Health") and entity.Health <= 0 : return False

    if "rx" in selector_var and entity.Rotation[1] > selector_var["rx"] : return False
    if "rxm" in selector_var and entity.Rotation[1] < selector_var["rxm"] : return False

    if "ry" in selector_var and entity.Rotation[0] > selector_var["ry"] : return False
    if "rym" in selector_var and entity.Rotation[0] < selector_var["rym"] : return False

    if "l" in selector_var and entity.PlayerLevel > selector_var["l"] : return False
    if "lm" in selector_var and entity.PlayerLevel < selector_var["lm"] : return False

    if "m_if" in selector_var and entity.GameMode not in selector_var["m_if"] : return False
    if "m_unless" in selector_var and entity.GameMode in selector_var["m_unless"] : return False

    if "type_if" in selector_var and entity.Identifier not in selector_var["type_if"] : return False
    if "type_unless" in selector_var and entity.Identifier in selector_var["type_unless"] : return False

    if "name_if" in selector_var and entity.CustomName.lower() not in selector_var["name_if"] : return False
    if "name_unless" in selector_var and entity.CustomName.lower() in selector_var["name_unless"] : return False

    if "tag_if" in selector_var :
        if "" in selector_var["tag_if"] and (len(selector_var["tag_if"]) > 1 or len(entity.Tags)) : return False
        elif "" not in selector_var["tag_if"] and any([ (i not in entity.Tags) for i in selector_var["tag_if"] ]) : return False
    if "tag_unless" in selector_var :
        if "" in selector_var["tag_unless"] and len(entity.Tags) == 0 : return False
        elif "" not in selector_var["tag_unless"] and any([ (i in entity.Tags) for i in selector_var["tag_unless"] ]) : return False

    if "family_if" in selector_var and any([ i not in entity.FamilyType for i in selector_var["family_if"] ]) : return False
    if "family_unless" in selector_var and any([ i in entity.FamilyType for i in selector_var["family_unless"] ]) : return False

    if "scores_if" in selector_var and not all((tools.scores_test(game_tread, i, entity, "if") for i in selector_var["scores_if"])) : return False
    if "scores_unless" in selector_var and not all((tools.scores_test(game_tread, i, entity, "unless") for i in selector_var["scores_unless"])) : return False

    if "permission_test" in selector_var and not all((selector_var["permission_test"][i] == entity.Permission[i] for i in selector_var["permission_test"])) : return False
    
    if "hasitem" in selector_var :
        hasitem_test_save:List[bool] = [] ; slot_item_save:List[BaseNbtClass.item_nbt] = []
        for item_test in selector_var["hasitem"] :
            slot_item_save.clear()
            for slot in item_test["location"] :
                if slot == "slot.weapon.mainhand" : item_list = [entity.Weapon[0]] if hasattr(entity, "Weapon") else []
                elif slot == "slot.weapon.offhand" : item_list = [entity.Weapon[1]] if hasattr(entity, "Weapon") else []
                elif slot == "slot.armor.head" : item_list = [entity.Armor[0]] if hasattr(entity, "Armor") else []
                elif slot == "slot.armor.chest" : item_list = [entity.Armor[1]] if hasattr(entity, "Armor") else []
                elif slot == "slot.armor.legs" : item_list = [entity.Armor[2]] if hasattr(entity, "Armor") else []
                elif slot == "slot.armor.feet" : item_list = [entity.Armor[3]] if hasattr(entity, "Armor") else []
                elif slot == "slot.enderchest" : item_list = entity.EnderChest if hasattr(entity, "EnderChest") else []
                elif slot == "slot.hotbar" : item_list = entity.HotBar if hasattr(entity, "HotBar") else []
                elif slot == "slot.inventory" : item_list = entity.Inventory["Items"] if hasattr(entity, "Inventory") else []
                elif slot == "slot.saddle" : item_list = [entity.Equippable[0]["Item"]] if hasattr(entity, "Equippable") else []
                elif slot == "slot.armor" : item_list = [entity.Equippable[1]["Item"]] if hasattr(entity, "Equippable") else []
                elif slot == "slot.chest" : item_list = entity.Inventory["Items"] if hasattr(entity, "Inventory") and hasattr(entity, "isChested") and entity.isChested else []
                elif slot == "slot.equippable" : item_list = [i["Item"] for i in entity.Equippable] if hasattr(entity, "Equippable") else []

                for slot_index,item in enumerate(item_list) :
                    if not isinstance(item, BaseNbtClass.item_nbt) : continue
                    if ("slot_unless" in item_test) and not(item_test["slot_unless"][0] <= slot_index <= item_test["slot_unless"][1]) : slot_item_save.append(item)
                    elif ("slot_unless" not in item_test) and item_test["slot_if"][0] <= slot_index <= item_test["slot_if"][1] : slot_item_save.append(item)

            item_count = 0
            item_id = item_test["item"] ; item_data = item_test["data"]
            test_item_obj = BaseNbtClass.item_nbt().__create__(item_id, 1, item_data if item_data != -1 else 0)
            for item_obj in slot_item_save :
                if item_obj.Identifier == test_item_obj.Identifier and \
                item_obj.Damage == test_item_obj.Damage : item_count += int(item_obj.Count)

            if ("quantity_unless" in item_test) and not(item_test["quantity_unless"][0] <= item_count <= item_test["quantity_unless"][1]) : hasitem_test_save.append(True)
            elif ("quantity_unless" not in item_test) and item_test["quantity_if"][0] <= item_count <= item_test["quantity_if"][1] : hasitem_test_save.append(True)
            else : hasitem_test_save.append(False)
        if not all(hasitem_test_save) : return False

    if "dx" in execute_var or "dy" in execute_var or "dz" in execute_var :
        if DIMENSION_LIST[entity.Dimension] != execute_var["dimension"] : return False
        dxdydz_test_area = [
            math.floor(origin[0]), math.floor(origin[0]) + 1,
            math.floor(origin[1]), math.floor(origin[1]) + 1,
            math.floor(origin[2]), math.floor(origin[2]) + 1
        ]
        if "dx" in execute_var : dxdydz_test_area[0 + int(selector_var["dx"] > 0)] += selector_var["dx"]
        if "dy" in execute_var is not None : dxdydz_test_area[2 + int(selector_var["dy"] > 0)] += selector_var["dy"]
        if "dz" in execute_var is not None : dxdydz_test_area[4 + int(selector_var["dz"] > 0)] += selector_var["dz"]
        if MathFunction.version_compare(execute_var["version"], (1,19,70)) == -1 :
            if not(dxdydz_test_area[0] <= entity.Pos[0] <= dxdydz_test_area[1]) : return False
            if not(dxdydz_test_area[2] <= entity.Pos[1] <= dxdydz_test_area[3]) : return False
            if not(dxdydz_test_area[4] <= entity.Pos[2] <= dxdydz_test_area[5]) : return False
        elif MathFunction.version_compare(execute_var["version"], (1,19,70)) >= 0 :
            if not(dxdydz_test_area[0]-entity.Collision['width']/2 <= entity.Pos[0] <= dxdydz_test_area[1]+entity.Collision['width']/2) : return False
            if not(dxdydz_test_area[4]-entity.Collision['width']/2 <= entity.Pos[2] <= dxdydz_test_area[5]+entity.Collision['width']/2) : return False
            if not(dxdydz_test_area[2]-entity.Collision['height'] <= entity.Pos[1] <= dxdydz_test_area[3]) : return False
        
    if "rm" in execute_var or "r" in execute_var :
        if DIMENSION_LIST[entity.Dimension] != execute_var["dimension"] : return False
        distance = DISTANCE_FUNC(entity, *origin)
        if "r" in selector_var and distance > selector_var["r"] : return False
        if "rm" in selector_var and distance < selector_var["rm"] : return False
    
    if "has_property" in execute_var :
        for condition in execute_var["has_property"] :
            if condition['condition'] == 'has_porperty' and not((condition['name'] in entity.porperty) ^ condition['not']) : return False
            if condition['condition'] == 'porperty_test' and ((condition['name'] not in entity.porperty) or 
            (condition['value'] is not None and type(condition['value']) != type(entity.porperty[condition['name']])) or 
            (condition['min'] is not None and type(condition['min']) != type(entity.porperty[condition['name']])) or 
            (condition['max'] is not None and type(condition['max']) != type(entity.porperty[condition['name']])) or
            (condition['value'] is not None and condition['value'] != entity.porperty[condition['name']]) or 
            (condition['min'] is not None and ((entity.porperty[condition['name']] < condition['min']) ^ condition['not'])) or
            (condition['max'] is not None and ((entity.porperty[condition['name']] > condition['max']) ^ condition['not']))) : return False

    return True



#@e
def RunTime_Selector_Entity(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, selector_var:dict, _except:BaseNbtClass.entity_nbt=None) :
    player_test = (selector_var.get("type_if", None) and "minecraft:player" in selector_var["type_if"]) or \
        any( (i in selector_var for i in ("m_if", "m_unless", "l", "lm", "permission_test")) )
    all_entity_test_list = game_tread.minecraft_chunk.__get_all_load_entity__(is_player=player_test)
    if _except and _except in all_entity_test_list : all_entity_test_list.remove(_except)
    entity_limit = selector_var["limit"] if "limit" in selector_var else 100000

    select_origin = (
       (np.float32(selector_var["pos_x"]) if selector_var["pos_x"][0] != "~" else (np.float32(selector_var["pos_x"][1:]) + execute_var["pos"][0])) if "pos_x" in selector_var else execute_var["pos"][0],
       (np.float32(selector_var["pos_y"]) if selector_var["pos_y"][0] != "~" else (np.float32(selector_var["pos_y"][1:]) + execute_var["pos"][1])) if "pos_y" in selector_var else execute_var["pos"][1],
       (np.float32(selector_var["pos_z"]) if selector_var["pos_z"][0] != "~" else (np.float32(selector_var["pos_z"][1:]) + execute_var["pos"][2])) if "pos_z" in selector_var else execute_var["pos"][2]
    )

    entity_saves : List[BaseNbtClass.entity_nbt] = [i for i in all_entity_test_list if Selector_Var_Condition_Test(execute_var, game_tread, select_origin, selector_var, i)]
    entity_list_result = sorted(
        entity_saves, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2])
    )

    if selector_var['sort'] == "nearest" : result = entity_list_result[0 : entity_limit]
    elif selector_var['sort'] == "farnest" : result = entity_list_result[-1 : (-entity_limit-1) : -1]

    if not result : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return result

#"player"
def RunTime_Selector_Name(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, name:str, _except:BaseNbtClass.entity_nbt=None) :
    all_entity_test_list = game_tread.minecraft_chunk.__get_all_load_entity__(is_player=True)
    if _except and _except in all_entity_test_list : all_entity_test_list.remove(_except)

    entity_saves : List[BaseNbtClass.entity_nbt] = [entity for entity in all_entity_test_list if name == entity.CustomName and entity.Health > 0]
        
    if not entity_saves : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return entity_saves

#@p
def RunTime_Selector_Player(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, selector_var:dict, _except:BaseNbtClass.entity_nbt=None) :
    all_entity_test_list = game_tread.minecraft_chunk.__get_all_load_entity__(is_player=True)
    if _except and _except in all_entity_test_list : all_entity_test_list.remove(_except)
    entity_limit = selector_var["limit"] if "limit" in selector_var else 1

    select_origin = (
       (np.float32(selector_var["pos_x"]) if selector_var["pos_x"][0] != "~" else (np.float32(selector_var["pos_x"][1:]) + execute_var["pos"][0])) if "pos_x" in selector_var else execute_var["pos"][0],
       (np.float32(selector_var["pos_y"]) if selector_var["pos_y"][0] != "~" else (np.float32(selector_var["pos_y"][1:]) + execute_var["pos"][1])) if "pos_y" in selector_var else execute_var["pos"][1],
       (np.float32(selector_var["pos_z"]) if selector_var["pos_z"][0] != "~" else (np.float32(selector_var["pos_z"][1:]) + execute_var["pos"][2])) if "pos_z" in selector_var else execute_var["pos"][2]
    )

    entity_saves : List[BaseNbtClass.entity_nbt] = [i for i in all_entity_test_list if Selector_Var_Condition_Test(execute_var, game_tread, select_origin, selector_var, i)]
    entity_list_result = sorted(
        entity_saves, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2])
    )

    if selector_var['sort'] == "nearest" : result = entity_list_result[0 : entity_limit]
    elif selector_var['sort'] == "farnest" : result = entity_list_result[-1 : (-entity_limit-1) : -1]

    if not result : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return result

#@a
def RunTime_Selector_All_Player(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, selector_var:dict, _except:BaseNbtClass.entity_nbt=None) :
    all_entity_test_list = game_tread.minecraft_chunk.__get_all_load_entity__(is_player=True)
    if _except and _except in all_entity_test_list : all_entity_test_list.remove(_except)
    entity_limit = selector_var["limit"] if "limit" in selector_var else 100000

    select_origin = (
       (np.float32(selector_var["pos_x"]) if selector_var["pos_x"][0] != "~" else (np.float32(selector_var["pos_x"][1:]) + execute_var["pos"][0])) if "pos_x" in selector_var else execute_var["pos"][0],
       (np.float32(selector_var["pos_y"]) if selector_var["pos_y"][0] != "~" else (np.float32(selector_var["pos_y"][1:]) + execute_var["pos"][1])) if "pos_y" in selector_var else execute_var["pos"][1],
       (np.float32(selector_var["pos_z"]) if selector_var["pos_z"][0] != "~" else (np.float32(selector_var["pos_z"][1:]) + execute_var["pos"][2])) if "pos_z" in selector_var else execute_var["pos"][2]
    )

    entity_saves : List[BaseNbtClass.entity_nbt] = [i for i in all_entity_test_list if Selector_Var_Condition_Test(execute_var, game_tread, select_origin, selector_var, i, is_alive=False)]
    entity_list_result = sorted(
        entity_saves, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2])
    )

    if selector_var['sort'] == "nearest" : result = entity_list_result[0 : entity_limit]
    elif selector_var['sort'] == "farnest" : result = entity_list_result[-1 : (-entity_limit-1) : -1]

    if not result : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return result

#@r
def RunTime_Selector_Random(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, selector_var:dict, _except:BaseNbtClass.entity_nbt=None) :
    player_test = ("type_if" not in selector_var or "minecraft:player" in selector_var["type_if"]) or \
        any( (i in selector_var for i in ("m_if", "m_unless", "l", "lm", "permission_test")) )
    all_entity_test_list = game_tread.minecraft_chunk.__get_all_load_entity__(is_player=player_test)
    if _except and _except in all_entity_test_list : all_entity_test_list.remove(_except)
    entity_limit = selector_var["limit"] if "limit" in selector_var else 1

    select_origin = (
       (np.float32(selector_var["pos_x"]) if selector_var["pos_x"][0] != "~" else (np.float32(selector_var["pos_x"][1:]) + execute_var["pos"][0])) if "pos_x" in selector_var else execute_var["pos"][0],
       (np.float32(selector_var["pos_y"]) if selector_var["pos_y"][0] != "~" else (np.float32(selector_var["pos_y"][1:]) + execute_var["pos"][1])) if "pos_y" in selector_var else execute_var["pos"][1],
       (np.float32(selector_var["pos_z"]) if selector_var["pos_z"][0] != "~" else (np.float32(selector_var["pos_z"][1:]) + execute_var["pos"][2])) if "pos_z" in selector_var else execute_var["pos"][2]
    )

    entity_saves : List[BaseNbtClass.entity_nbt] = [i for i in all_entity_test_list if Selector_Var_Condition_Test(execute_var, game_tread, select_origin, selector_var, i)]
    entity_list_result = sorted(
        entity_saves, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2])
    )
    random.shuffle(entity_list_result)
    result = entity_list_result[0 : entity_limit]

    if not result : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return result

#@s
def RunTime_Selector_Self(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, selector_var:dict, _except:BaseNbtClass.entity_nbt=None, is_player:bool=False, is_npc:bool=False) :
    all_entity_test_list = [execute_var["executer"]] if isinstance(execute_var["executer"], BaseNbtClass.entity_nbt) else []
    if _except and _except in all_entity_test_list : all_entity_test_list.remove(_except)
    if is_npc and all_entity_test_list and all_entity_test_list[0].Identifier != "minecraft:npc" : all_entity_test_list.pop()
    if is_player and all_entity_test_list and all_entity_test_list[0].Identifier != "minecraft:player" : all_entity_test_list.pop()

    select_origin = (
       (np.float32(selector_var["pos_x"]) if selector_var["pos_x"][0] != "~" else (np.float32(selector_var["pos_x"][1:]) + execute_var["pos"][0])) if "pos_x" in selector_var else execute_var["pos"][0],
       (np.float32(selector_var["pos_y"]) if selector_var["pos_y"][0] != "~" else (np.float32(selector_var["pos_y"][1:]) + execute_var["pos"][1])) if "pos_y" in selector_var else execute_var["pos"][1],
       (np.float32(selector_var["pos_z"]) if selector_var["pos_z"][0] != "~" else (np.float32(selector_var["pos_z"][1:]) + execute_var["pos"][2])) if "pos_z" in selector_var else execute_var["pos"][2]
    )

    entity_saves : List[BaseNbtClass.entity_nbt] = [i for i in all_entity_test_list if Selector_Var_Condition_Test(execute_var, game_tread, select_origin, selector_var, i, is_alive=False)]

    if not entity_saves : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return entity_saves

#@initiator
def RunTime_Selector_Initiator(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread) :
    return Response.Response_Template("没有与目标选择器匹配的目标").substitute()



def set_insert_extand_Data(saves:dict, key:str, value, types:Union[list,None]=None) :
    if key not in saves :
        if types is None : saves[key] = value
        else : saves[key] = [value]
    else :
        if isinstance(saves[key], dict) : saves[key].update(value)
        elif isinstance(saves[key], list) and value not in saves[key] : saves[key].append(value)
        elif not isinstance(saves[key], (dict,list)) : saves[key] = value

def Selector_Save_Set(game_tread:RunTime.minecraft_thread, selector_save:dict, token_list:COMMAND_TOKEN, index:int) -> int :
    selector_argument = token_list[index]["token"].group()

    if selector_argument in ("x","y","z") :
        key = "pos_%s" % selector_argument ; index += 2
        if token_list[index]["type"] == "Value" : 
            selector_save[key] = token_list[index]["token"].group()
        elif token_list[index]["type"] == "Relative_Value" and len(token_list[index]["token"].group()) > 1 : 
            selector_save[key] = token_list[index]["token"].group()

    if selector_argument in ("dx","dy","dz","rxm","rx","rym","ry") :
        index += 2 ; selector_save[selector_argument] = token_list[index]["token"].group()

    elif selector_argument in ("lm","l") :
        index += 2 ; selector_save[selector_argument] = int(token_list[index]["token"].group())
        if selector_save[selector_argument] < 0 : 
            raise CompileError("等级参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))
    
    elif selector_argument in ("rm","r") :
        index += 2 ; selector_save[selector_argument] = np.float32(token_list[index]["token"].group())
        if selector_save[selector_argument] < 0 : 
            raise CompileError("距离参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))

    elif selector_argument == "c" :
        index += 2 ; selector_save["limit"] = int(token_list[index]["token"].group())
        if selector_save["limit"] == 0 :
            raise CompileError("数量参数不能为0",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))
        elif selector_save["limit"] < 0 : selector_save["sort"] = "farnest"

    elif selector_argument == "scores" :
        index += 2
        while token_list[index]["type"] != "End_Score_Argument" :
            index += 1
            if token_list[index]["type"] == "Next_Score_Argument" : continue

            board_condition = {"board":"", "min":-2147483648, "max":2147483647}
            board_condition["board"] = Quotation_String_transfor_2(token_list[index]["token"].group())

            index += 2 ; unless_mode = False
            if token_list[index]["type"] == "Not" : unless_mode = True ; index += 1
            if token_list[index]["type"] == "Range_Min" : 
                board_condition["min"] = int(token_list[index]["token"].group()) ; index += 1

            if token_list[index]["type"] != "Range_Sign" : board_condition["max"] = board_condition["min"]
            else :
                index += 1
                if token_list[index]["type"] == "Range_Max" : 
                    board_condition["max"] = int(token_list[index]["token"].group()) ; index += 1
            
            if unless_mode : set_insert_extand_Data(selector_save, "scores_unless", board_condition, list)
            else : set_insert_extand_Data(selector_save, "scores_if", board_condition, list)
    
    elif selector_argument == "haspermission" :
        index += 2
        while token_list[index]["type"] != "End_Permission_Argument" :
            index += 1
            permission = token_list[index]["token"].group()
            if "permission_test" not in selector_save : selector_save["permission_test"] = {}
            selector_save["permission_test"][permission] = token_list[index+2]["token"].group()
            index += 3

    elif selector_argument == "hasitem" :

        def read_hasitem_condition(index:int) -> int :
            hasitem_condition = {
                "item":"", "data":0, "location":["slot.armor.head","slot.armor.chest","slot.armor.legs",
                "slot.armor.feet","slot.hotbar","slot.inventory","slot.weapon.offhand"],
                "slot_if":[0,2147483647], "quantity_if":[1,2147483647]
            }
            has_location = False ; has_slot = False
            while token_list[index]["type"] != "End_Item_Argument" :
                index += 1
                if token_list[index]["type"] == "Next_Item_Argument" : continue

                if token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "item" :
                    index += 2
                    item_name = minecraft_ID_transfor(token_list[index]["token"].group())
                    if item_name not in game_tread.minecraft_ident.items : raise CompileError("不存在的物品ID：%s" % item_name, 
                        pos=(token_list[index]["token"].start(),token_list[index]["token"].end()))
                    hasitem_condition["item"] = item_name
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "data" :
                    index += 2
                    data_value = int(token_list[index]["token"].group())
                    hasitem_condition["data"] = data_value
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "quantity" :
                    index += 2 ; unless_mode = False ; quantity = [1,2147483647]
                    if token_list[index]["type"] == "Not" : unless_mode = True ; index += 1
                    if token_list[index]["type"] == "Range_Min" : 
                        quantity[0] = int(token_list[index]["token"].group()) ; index += 1

                    if token_list[index]["type"] != "Range_Sign" : quantity[1] = quantity[0]
                    else :
                        index += 1
                        if token_list[index]["type"] == "Range_Max" : 
                            quantity[1] = int(token_list[index]["token"].group()) ; index += 1
                    
                    if unless_mode : hasitem_condition["quantity_unless"] = quantity
                    else : hasitem_condition["quantity_if"] = quantity
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "location" :
                    has_location = True ; index += 2
                    hasitem_condition["location"].clear()
                    hasitem_condition["location"].append(token_list[index]["token"].group())
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "slot" :
                    has_slot = True ; index += 2 ; unless_mode = False ; slot = [1,2147483647]
                    if token_list[index]["type"] == "Not" : unless_mode = True ; index += 1
                    if token_list[index]["type"] == "Range_Min" : 
                        slot[0] = int(token_list[index]["token"].group()) ; index += 1

                    if token_list[index]["type"] != "Range_Sign" : slot[1] = slot[0]
                    else :
                        index += 1
                        if token_list[index]["type"] == "Range_Max" : 
                            slot[1] = int(token_list[index]["token"].group()) ; index += 1
                    if unless_mode : hasitem_condition["slot_unless"] = slot
                    else : hasitem_condition["slot_if"] = slot

            if not has_location and has_slot : raise CompileError("hasitem的location参数不存在，slot参数指定无效")
            if hasitem_condition["item"] == "" : raise CompileError("hasitem中未指定item参数")
            set_insert_extand_Data(selector_save, "hasitem", hasitem_condition, list)
            return index

        index += 2
        if token_list[index]["type"] != "Start_Item_Condition" : index = read_hasitem_condition(index)
        else : 
            while token_list[index]["type"] != "End_Item_Condition" :
                index += 1 ; index = read_hasitem_condition(index) ; index += 1
        #print( selector_save, token_list[index] )

    elif selector_argument in ("tag","name","family","type","m") :
        index += 2 ; mode = ("%s_if" if token_list[index]["type"] != "Not" else "%s_unless") % selector_argument
        if token_list[index]["type"] == "Not" : index += 1
        if selector_argument == "tag" and token_list[index]["type"] in ("Next_Selector_Argument", "End_Selector_Argument") :
            set_insert_extand_Data(selector_save, mode, "", list)
            index -= 1
        else : 
            str1 = Quotation_String_transfor_2( token_list[index]["token"].group())
            if selector_argument == "type" : 
                str1 = minecraft_ID_transfor(str1)
                if str1 not in game_tread.minecraft_ident.entities : 
                    raise CompileError("不存在的实体ID：%s" % str1,pos=(token_list[index]["token"].start(),token_list[index]["token"].end()))
            set_insert_extand_Data(selector_save, mode, str1, list)

    elif selector_argument == "has_property" :
        index += 3
        while 1 :
            if token_list[index]["type"] == "End_Property_Argument" : break
            if token_list[index]["type"] == "Next_Property_Argument" : index += 1
            if token_list[index]["type"] == "Property_Argument" : 
                index += 2
                condition_json = {"condition":"has_porperty", "name":"", "not":False}
                if token_list[index]["type"] == "Not" : condition_json["not"] = True ; index += 1
                condition_json["name"] = name = token_list[index]["token"].group() ; index += 1
                if not any( (name in data["description"].get("properties", {}) \
                    for entity,data in game_tread.minecraft_ident.entities.items()) ) :
                    raise CompileError("不存在的实体属性：%s" % name, pos=(token_list[index-1]["token"].start(),token_list[index-1]["token"].end()))
                set_insert_extand_Data(selector_save, "has_porperty", condition_json, list)
            elif token_list[index]["type"] == "Property" : 
                condition_json = {"condition":"porperty_test", "name":"", "value":None, "min":None, "max":None, "not":False}
                condition_json["name"] = name = token_list[index]["token"].group() ; index += 2
                if not any( (name in data["description"].get("properties", {}) \
                    for entity,data in game_tread.minecraft_ident.entities.items()) ) :
                    raise CompileError("不存在的实体属性：%s" % name, pos=(token_list[index-2]["token"].start(),token_list[index-2]["token"].end()))
                if token_list[index]["type"] == "Bool" :
                    condition_json["value"] = ("false","true").index(token_list[index]["token"].group()).__bool__() ; index += 1
                elif token_list[index]["type"] == "Float" :
                    condition_json["value"] = float(token_list[index]["token"].group()) ; index += 1
                elif token_list[index]["type"] == "String" :
                    condition_json["value"] = Quotation_String_transfor_2(token_list[index]["token"].group()) ; index += 1
                else :
                    if token_list[index]["type"] == "Not" : condition_json["not"] = True ; index += 1
                    if token_list[index]["type"] == "Range_Min" : 
                        condition_json["min"] = int(token_list[index]["token"].group()) ; index += 1
                    if token_list[index]["type"] != "Range_Sign" : condition_json["max"] = condition_json["min"]
                    else :
                        index += 1
                        if token_list[index]["type"] == "Range_Max" : 
                            condition_json["max"] = int(token_list[index]["token"].group()) ; index += 1

                set_insert_extand_Data(selector_save, "has_porperty", condition_json, list)

    return index + 1

def Selector_Compiler(game_tread:RunTime.minecraft_thread, token_list:COMMAND_TOKEN, index:int, / ,
                      is_player:bool=False, is_npc:bool=False, is_single=False) -> Tuple[int, functools.partial] : 

    start_index_save = token_list[index]["token"].start()
    selector_argument_all = ("x", "y", "z", "c", "dx", "dy", "dz", "rx", "ry", "rxm", "rym", "l", "lm", "r", "rm", "scores",
                             "hasitem", "haspermission", "has_property", "tag", "name", "family", "type", "m")
    selector_argument_single = ("x","y","z","c","dx","dy","dz","rx","ry","rxm","rym","l","lm","r","rm","scores","hasitem",
                                "haspermission", "has_property")
    selector_argument_count = { i:0 for i in selector_argument_all }
    selector_save = {"sort":"nearest"}
    """
    {
        "pos_x": str, "pos_y": str, "pos_z": str, "limit":int, "sort":nearest|farnest, 
        "dx": float, "dy": float, "dz": float, "rx": float, "rxm": float, "ry": float, "rym": float,
        "l": float, "lm": float, "r": float, "rm": float, "scores_if":[], "scores_unless":[], "tag_if":[], "tag_unless":[],
        "family_if":[], "family_unless":[], "m_if":[], "m_unless":[], "name_if":[], "name_unless":[], "type_if":[], "type_unless":[],
        "hasitem":[], "permission_test":{}, "has_porperty":[]
    }
    """

    if token_list[index]["type"] == "Player_Name" :
        player_name = Quotation_String_transfor_2(token_list[index]["token"].group().lower())
        return functools.partial(RunTime_Selector_Name, name=player_name)

    Selector_Var = token_list[index]["token"].group()
    if Selector_Var == "@p" : selector_func = RunTime_Selector_Player ; is_player = True
    elif Selector_Var == "@a" : selector_func = RunTime_Selector_All_Player ; is_player = True
    elif Selector_Var == "@r" : selector_func = RunTime_Selector_Random
    elif Selector_Var == "@e" : selector_func = RunTime_Selector_Entity
    elif Selector_Var == "@s" : selector_func = RunTime_Selector_Self
    elif Selector_Var == "@initiator" : return (index+1, RunTime_Selector_Initiator)

    has_selector_arg_test = False ; check_sum = 0
    if (index+1) < token_list.__len__() and token_list[index+1]["type"] == "Start_Selector_Argument" :
        has_selector_arg_test = True
        iter1 = itertools.takewhile(lambda x: x["type"] != "End_Selector_Argument", token_list[index+2:])
        list1 = [ abs(hash(i["token"].group())) for i in iter1 ] ; check_sum = sum(list1)
        if check_sum in SELECTOR_VAR_MEMEROY : 
            selector_save = SELECTOR_VAR_MEMEROY[check_sum]
            has_selector_arg_test = False
            index += 2 + len(list1)
        else : index += 1
    else : selector_save = SELECTOR_VAR_MEMEROY[check_sum]

    while has_selector_arg_test and token_list[index]["type"] != "End_Selector_Argument" :
        index += 1
        if token_list[index]["type"] == "Next_Selector_Argument" : continue
        if token_list[index]["type"] == "Selector_Argument" : 
            selector_argument_token = token_list[index]["token"]
            selector_argument = selector_argument_token.group()
            selector_argument_count[selector_argument] += 1
            if any( (selector_argument_count[i] > 1 for i in selector_argument_single) ) :
                raise CompileError("重复的选择器 %s 参数" % selector_argument, 
                pos=(selector_argument_token.start(),selector_argument_token.end()))
            index = Selector_Save_Set(game_tread, selector_save, token_list, index)
    if has_selector_arg_test : SELECTOR_VAR_MEMEROY[check_sum] = selector_save

    end_index_save = token_list[index]["token"].end()
    if is_single and (("limit" in selector_save and selector_save["limit"] > 1) or ("limit" not in selector_save and Selector_Var in "@a@e")) : 
        raise CompileError("选择器无法选择多个实体", pos=(start_index_save, end_index_save))
    if is_player and Selector_Var != "@s" and (("type_if" in selector_save and selector_save["type_if"][0] != "minecraft:player") or (
        "type_if" not in selector_save and Selector_Var == "@e") ) : 
        raise CompileError("选择器只能为玩家类型", pos=(start_index_save, end_index_save))
    if is_npc and Selector_Var != "@s" and (("type_if" in selector_save and selector_save["type_if"][0] != "minecraft:npc") or (
        "type_if" not in selector_save) ) : 
        raise CompileError("选择器只能为NPC类型", pos=(start_index_save, end_index_save))
    if "r" in selector_save and "rm" in selector_save and selector_save["rm"] > selector_save["r"] : 
        raise CompileError("距离参数上限不能小于下限", pos=(start_index_save, end_index_save))
    if "l" in selector_save and "lm" in selector_save and selector_save["lm"] > selector_save["l"] : 
        raise CompileError("等级参数上限不能小于下限", pos=(start_index_save, end_index_save))

    if "name_if" in selector_save and len(selector_save["name_if"]) > 1 : 
        raise CompileError("选择器参数 name 具有重复指定的正选条件", pos=(start_index_save, end_index_save))
    if "name_if" in selector_save and "name_unless" in selector_save and len(selector_save["name_if"]) > 0 and len(selector_save["name_unless"]) > 0 : 
        raise CompileError("选择器参数 name 同时存在正反选条件", pos=(start_index_save, end_index_save))
    if "type_if" in selector_save and len(selector_save["type_if"]) > 1 : 
        raise CompileError("选择器参数 type 具有重复指定的正选条件", pos=(start_index_save, end_index_save))
    if "type_if" in selector_save and "type_unless" in selector_save and len(selector_save["type_if"]) > 0 and len(selector_save["type_unless"]) > 0 :
        raise CompileError("选择器参数 type 同时存在正反选条件", pos=(start_index_save, end_index_save))
    if "m_if" in selector_save and len(selector_save["m_if"]) > 1 : 
        raise CompileError("选择器参数 m 具有重复指定的正选条件", pos=(start_index_save, end_index_save))
    if "m_if" in selector_save and "m_unless" in selector_save and len(selector_save["m_if"]) > 0 and len(selector_save["m_unless"]) > 0 :
        raise CompileError("选择器参数 m 同时存在正反选条件", pos=(start_index_save, end_index_save))
    
    if selector_func is RunTime_Selector_Random and selector_save["sort"] == "farnest" :
        raise CompileError("随机选择器的数量参数不能为负数", pos=(start_index_save, end_index_save))

    print(selector_save)
    if selector_func is not RunTime_Selector_Self : return (index+1, functools.partial(selector_func, selector_var=selector_save))
    else : return (index+1, functools.partial(selector_func, selector_var=selector_save, is_npc=is_npc, is_player=is_player))





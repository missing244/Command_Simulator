from typing import Dict,Union,List,Tuple,Literal
from ... import RunTime,BaseNbtClass,MathFunction,np,Constants
from .. import COMMAND_CONTEXT,Response
from . import CompileError
import re,functools,math,random

DIMENSION_LIST= list(Constants.DIMENSION_INFO)
DISTANCE_FUNC = lambda item,origin_x,origin_y,origin_z : ((item.Pos[0]-origin_x)**2 + (item.Pos[1]-origin_y)**2 + (item.Pos[2]-origin_z)**2) ** 0.5




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

def RunTime_Selector(execute_var:COMMAND_CONTEXT, game_tread:RunTime.minecraft_thread, selector_var:dict) :
    entity_saves : List[BaseNbtClass.entity_nbt] = []
    if selector_var["is_executer"] : all_entity_test_list = (execute_var["executer"],) if isinstance(execute_var["executer"],BaseNbtClass.entity_nbt) else ()
    else : all_entity_test_list = game_tread.minecraft_chunk.__get_all_load_entity__()

    select_origin_x = (execute_var["pos"][0] + selector_var["pos_offset"][0]) if selector_var["pos"][0] == None else (selector_var["pos"][0] + selector_var["pos_offset"][0])
    select_origin_y = (execute_var["pos"][1] + selector_var["pos_offset"][1]) if selector_var["pos"][1] == None else (selector_var["pos"][1] + selector_var["pos_offset"][1])
    select_origin_z = (execute_var["pos"][2] + selector_var["pos_offset"][2]) if selector_var["pos"][2] == None else (selector_var["pos"][2] + selector_var["pos_offset"][2])

    for entity in all_entity_test_list :
        if selector_var["is_alive"] and hasattr(entity,"Health") and entity.Health <= 0 : continue
        if not(selector_var["rotate_y"][0] <= entity.Rotation[0] <= selector_var["rotate_y"][1]): continue
        if not(selector_var["rotate_x"][0] <= entity.Rotation[0] <= selector_var["rotate_x"][1]): continue

        if selector_var["level"] :
            if entity.Identifier != "minecraft:player" : continue
            if not(selector_var["level"][0] <= entity.Level["value"] <= selector_var["level"][1]) : continue

        if (selector_var["m_if"] or selector_var["m_unless"]) : 
            if entity.Identifier != "minecraft:player" : continue
            if selector_var["m_if"] and entity.GameMode not in selector_var["m_if"] : continue
            if selector_var["m_unless"] and entity.GameMode in selector_var["m_unless"] : continue

        if selector_var["type_if"] and entity.Identifier not in selector_var["type_if"] : continue
        if selector_var["type_unless"] and entity.Identifier in selector_var["type_unless"] : continue

        if selector_var["name_if"] and entity.CustomName.lower() not in selector_var["name_if"] : continue
        if selector_var["name_unless"] and entity.CustomName.lower() in selector_var["name_unless"] : continue

        if selector_var["tag_if"] :
            if "" in selector_var["tag_if"] and (len(selector_var["tag_if"]) > 1 or len(entity.Tags)) : continue
            elif "" not in selector_var["tag_if"] and any([ (i not in entity.Tags) for i in selector_var["tag_if"] ]) : continue
        if selector_var["tag_unless"] :
            if "" in selector_var["tag_unless"] and len(entity.Tags) == 0 : continue
            elif "" not in selector_var["tag_unless"] and any([ (i in entity.Tags) for i in selector_var["tag_unless"] ]) : continue

        if selector_var["family_if"] and any([ i not in entity.FamilyType for i in selector_var["family_if"] ]) : continue
        if selector_var["family_unless"] and any([ i in entity.FamilyType for i in selector_var["family_unless"] ]) : continue

        if selector_var["scores_if"] and not all([tools.scores_test(game_tread, i, entity, "if") for i in selector_var["scores_if"]]) : continue
        if selector_var["scores_unless"] and not all([tools.scores_test(game_tread, i, entity, "unless") for i in selector_var["scores_unless"]]) : continue
        
        if selector_var["permission_test"] and entity.Identifier != "minecraft:player" : continue
        if selector_var["permission_test"] and not all([selector_var["permission_test"][i] == entity.Permission[i] for i in selector_var["permission_test"]]) : continue
       
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
                elif slot == "slot.armor.enderchest" : item_list = entity.EnderChest if hasattr(entity, "EnderChest") else []
                elif slot == "slot.armor.hotbar" : item_list = entity.HotBar if hasattr(entity, "HotBar") else []
                elif slot == "slot.armor.inventory" : item_list = entity.Inventory["Items"] if hasattr(entity, "Inventory") else []
                elif slot == "slot.armor.saddle" : item_list = [entity.Equippable[0]["Item"]] if hasattr(entity, "Equippable") else []
                elif slot == "slot.armor.armor" : item_list = [entity.Equippable[1]["Item"]] if hasattr(entity, "Equippable") else []
                elif slot == "slot.chest" : item_list = entity.Inventory["Items"] if hasattr(entity, "Inventory") and hasattr(entity, "isChested") and entity.isChested else []
                elif slot == "slot.equippable" : item_list = [i["Item"] for i in entity.Equippable] if hasattr(entity, "Equippable") else []

                for slot_index,item in enumerate(item_list) :
                    if not isinstance(item, BaseNbtClass.item_nbt) : continue
                    if ("slot_unless" in item_test) and not(item_test["slot_unless"][0] <= slot_index <= item_test["slot_unless"][1]) : slot_item_save.append(item)
                    elif ("slot_unless" not in item_test) and item_test["slot_if"][0] <= slot_index <= item_test["slot_if"][1] : slot_item_save.append(item)

            item_count = 0
            for item_obj in slot_item_save :
                if item_obj.Identifier == item_test["item"] and item_obj.Damage == item_test["data"] : item_count += int(item_obj.Count)
            
            if ("quantity_unless" in item_test) and not(item_test["quantity_unless"][0] <= slot_index <= item_test["quantity_unless"][1]) : hasitem_test_save.append(True)
            elif ("quantity_unless" not in item_test) and item_test["quantity_if"][0] <= slot_index <= item_test["quantity_if"][1] : hasitem_test_save.append(True)
            else : hasitem_test_save.append(False)
        if not all(hasitem_test_save) : continue

        if any([i != None for i in selector_var["dxdydz"]]) and MathFunction.version_compare(execute_var["version"], (1,19,70)) == -1 :
            if DIMENSION_LIST[entity.Dimension] != execute_var["dimension"] : continue
            dxdydz_test_area = [
                math.floor(select_origin_x), math.floor(select_origin_x) + 1,
                math.floor(select_origin_y), math.floor(select_origin_y) + 1,
                math.floor(select_origin_z), math.floor(select_origin_z) + 1
            ]
            if selector_var["dxdydz"][0] != None : dxdydz_test_area[0 + int(selector_var["dxdydz"][0] > 0)] += selector_var["dxdydz"][0]
            if selector_var["dxdydz"][1] != None : dxdydz_test_area[2 + int(selector_var["dxdydz"][1] > 0)] += selector_var["dxdydz"][1]
            if selector_var["dxdydz"][2] != None : dxdydz_test_area[4 + int(selector_var["dxdydz"][2] > 0)] += selector_var["dxdydz"][2]

            if not(dxdydz_test_area[0] <= entity.Pos[0] <= dxdydz_test_area[1]) : continue
            if not(dxdydz_test_area[2] <= entity.Pos[1] <= dxdydz_test_area[3]) : continue
            if not(dxdydz_test_area[4] <= entity.Pos[2] <= dxdydz_test_area[5]) : continue
        if any([i != None for i in selector_var["dxdydz"]]) and MathFunction.version_compare(execute_var["version"], (1,19,70)) >= 0 :
            if DIMENSION_LIST[entity.Dimension] != execute_var["dimension"] : continue
            dxdydz_test_area = [
                select_origin_x, select_origin_x + 1,
                select_origin_y, select_origin_y + 1,
                select_origin_z, select_origin_z + 1
            ]
            if selector_var["dxdydz"][0] != None : dxdydz_test_area[0 + int(selector_var["dxdydz"][0] > 0)] += selector_var["dxdydz"][0]
            if selector_var["dxdydz"][1] != None : dxdydz_test_area[2 + int(selector_var["dxdydz"][1] > 0)] += selector_var["dxdydz"][1]
            if selector_var["dxdydz"][2] != None : dxdydz_test_area[4 + int(selector_var["dxdydz"][2] > 0)] += selector_var["dxdydz"][2]

            #print(dxdydz_m1,selector_var["dxdydz"])
            if not(dxdydz_test_area[0]-entity.Collision['width']/2 <= entity.Pos[0] <= dxdydz_test_area[1]+entity.Collision['width']/2) : continue
            if not(dxdydz_test_area[4]-entity.Collision['width']/2 <= entity.Pos[2] <= dxdydz_test_area[5]+entity.Collision['width']/2) : continue
            if not(dxdydz_test_area[2]-entity.Collision['height'] <= entity.Pos[1] <= dxdydz_test_area[3]) : continue
        
        if selector_var["distance"] :
            if DIMENSION_LIST[entity.Dimension] != execute_var["dimension"] : continue
            if not(selector_var["distance"][0] <= DISTANCE_FUNC(entity,select_origin_x,select_origin_y,select_origin_z) <= selector_var["distance"][1]) : continue

        entity_saves.append(entity)
    
    entity_list_result = sorted(
        [i for i in entity_saves], key=functools.partial(DISTANCE_FUNC, origin_x=select_origin_x,
        origin_y=select_origin_y, origin_z=select_origin_z)
    )
    if selector_var['sort'] == "random" : random.shuffle(entity_list_result)

    if selector_var['sort'] == "nearest" : result = entity_list_result[0 : selector_var['limit'] : 1]
    elif selector_var['sort'] == "farnest" : result = entity_list_result[-1 : (-selector_var['limit']-1) : -1]
    elif selector_var['sort'] == "random" : result = entity_list_result[0 : selector_var['limit']]

    if not result : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
    else : return result

def Selector_Save_Set(game_tread:RunTime.minecraft_thread, selector_save:dict, 
                      token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]], index:int) -> int :
    selector_argument = token_list[index]["token"].group()

    if selector_argument in ("x","y","z") :
        search_index = ("x","y","z") ; index += 2
        set_index = search_index.index(selector_argument)
        if token_list[index]["type"] == "Value" : 
            selector_save["pos"][set_index] = np.float32(token_list[index]["token"].group())
        elif token_list[index]["type"] == "Relative_Value" : 
            selector_save["pos_offset"][set_index] = np.float32(token_list[index]["token"].group()[1:])

    elif selector_argument in ("dx","dy","dz") :
        search_index = ("dx","dy","dz") ; index += 2
        set_index = search_index.index(selector_argument)
        selector_save["dxdydz"][set_index] = np.float32(token_list[index]["token"].group())

    elif selector_argument in ("rxm","rx") :
        search_index = ("rxm","rx") ; index += 2
        set_index = search_index.index(selector_argument)
        selector_save["rotate_x"][set_index] = np.float32(token_list[index]["token"].group())

    elif selector_argument in ("rym","ry") :
        search_index = ("rym","ry") ; index += 2
        set_index = search_index.index(selector_argument)
        selector_save["rotate_y"][set_index] = np.float32(token_list[index]["token"].group())

    elif selector_argument in ("lm","l") :
        search_index = ("lm","l") ; index += 2
        if selector_save["level"] == None : selector_save["level"] = [0, 2147483647]
        set_index = search_index.index(selector_argument)
        selector_save["level"][set_index] = int(token_list[index]["token"].group())
        if selector_save["level"][set_index] < 0 : 
            raise CompileError("等级参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))
    
    elif selector_argument in ("rm","r") :
        search_index = ("rm","r") ; index += 2
        if selector_save["distance"] == None : selector_save["distance"] = [0.0, 2147483647.0]
        set_index = search_index.index(selector_argument)
        selector_save["distance"][set_index] = np.float32(token_list[index]["token"].group())
        if selector_save["distance"][set_index] < 0 : 
            raise CompileError("距离参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))

    elif selector_argument == "c" :
        index += 2
        selector_save["limit"] = int(token_list[index]["token"].group())
        if selector_save["sort"] == "random" and selector_save["limit"] < 0 :
            raise CompileError("随机选择器的数量参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))

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
                board_condition["min"] = int(token_list[index]["token"].group())
                index += 1

            if token_list[index]["type"] != "Range_Sign" : board_condition["max"] = board_condition["min"]
            else :
                index += 1
                if token_list[index]["type"] == "Range_Max" : 
                    board_condition["max"] = int(token_list[index]["token"].group())
                    index += 1
            
            if unless_mode : selector_save["scores_unless"].append(board_condition)
            else : selector_save["scores_if"].append(board_condition)
    
    elif selector_argument == "haspermission" :
        index += 2
        while token_list[index]["type"] != "End_Permission_Argument" :
            index += 1
            selector_save["permission_test"][token_list[index]["token"].group()] = token_list[index+2]["token"].group()
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
                    if item_name not in game_tread.minecraft_ident.items : 
                        raise CompileError("不存在的物品ID",pos=(token_list[index]["token"].start(),token_list[index]["token"].end()))
                    hasitem_condition["item"] = item_name
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "data" :
                    index += 2
                    data_value = int(token_list[index]["token"].group())
                    hasitem_condition["data"] = data_value
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "quantity" :
                    index += 2 ; unless_mode = False ; quantity = [1,2147483647]
                    if token_list[index]["type"] == "Not" : unless_mode = True ; index += 1
                    if token_list[index]["type"] == "Range_Min" : 
                        quantity[0] = int(token_list[index]["token"].group())
                        index += 1

                    if token_list[index]["type"] != "Range_Sign" : quantity[1] = quantity[0]
                    else :
                        index += 1
                        if token_list[index]["type"] == "Range_Max" : 
                            quantity[1] = int(token_list[index]["token"].group()) ; index += 1
                    
                    if unless_mode : hasitem_condition["quantity_unless"] = quantity
                    else : hasitem_condition["quantity_if"] = quantity
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "location" :
                    has_location = True
                    index += 2
                    hasitem_condition["location"].clear()
                    hasitem_condition["location"].append(token_list[index]["token"].group())
                elif token_list[index]["type"] == "Item_Argument" and token_list[index]["token"].group() == "slot" :
                    has_slot = True ; index += 2 ; unless_mode = False ; slot = [1,2147483647]
                    if token_list[index]["type"] == "Not" : unless_mode = True ; index += 1
                    if token_list[index]["type"] == "Range_Min" : 
                        slot[0] = int(token_list[index]["token"].group())
                        index += 1

                    if token_list[index]["type"] != "Range_Sign" : slot[1] = slot[0]
                    else :
                        index += 1
                        if token_list[index]["type"] == "Range_Max" : 
                            slot[1] = int(token_list[index]["token"].group()) ; index += 1
                    if unless_mode : hasitem_condition["slot_unless"] = slot
                    else : hasitem_condition["slot_if"] = slot

            if not has_location and has_slot : raise CompileError("hasitem的location参数不存在，slot参数指定无效")
            if hasitem_condition["item"] == "" : raise CompileError("hasitem中未指定item参数")
            selector_save["hasitem"].append(hasitem_condition)
            return index

        index += 2
        if token_list[index]["type"] != "Start_Item_Condition" : index = read_hasitem_condition(index)
        else : 
            while token_list[index]["type"] != "End_Item_Condition" :
                index += 1 ; index = read_hasitem_condition(index) ; index += 1
        print( selector_save, token_list[index] )

    elif selector_argument in ("tag","name","family","type","m") :
        index += 2 ; mode = "%s_if" if token_list[index]["type"] != "Not" else "%s_unless"
        if token_list[index]["type"] == "Not" : index += 1
        if selector_argument == "tag" and token_list[index]["type"] in ("Next_Selector_Argument", "End_Selector_Argument") :
            selector_save[mode % selector_argument].append("")
            index -= 1
        else : 
            str1 = Quotation_String_transfor_2( token_list[index]["token"].group())
            if selector_argument == "type" : str1 = minecraft_ID_transfor(str1)
            selector_save[mode % selector_argument].append(str1)

    return index + 1

def Selector_Compiler(game_tread:RunTime.minecraft_thread, token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]], index:int, / ,
                      is_player:bool=False, is_npc:bool=False, is_single=False) -> Tuple[int, functools.partial] : 

    start_index_save = token_list[index]["token"].start()
    selector_argument_all = ("x", "y", "z", "c", "dx", "dy", "dz", "rx", "ry", "rxm", "rym", "l", "lm", "r", "rm", "scores",
                             "hasitem", "haspermission", "tag", "name", "family", "type", "m")
    selector_argument_single = ("x","y","z","c","dx","dy","dz","rx","ry","rxm","rym","l","lm","r","rm","scores","hasitem","haspermission")
    selector_argument_count = { i:0 for i in selector_argument_all }
    selector_save = {
        "pos":[None, None, None], "pos_offset":[0, 0, 0], "dxdydz":[None, None, None],
        "distance":None, "rotate_x":[-90.0, 90.0], "rotate_y":[-180.0, 180.0], "level": None,
        "scores_if":[], "scores_unless":[], "tag_if":[],"tag_unless":[], "family_if":[], "family_unless":[],
        "m_if":[], "m_unless":[], "name_if":[], "name_unless":[], "type_if":[], "type_unless":[],
        "hasitem":[], "permission_test":{},
        "limit":200000, "sort":"nearest", "is_alive":True, "is_executer":False
    }

    if token_list[index]["type"] == "Player_Name" :
        selector_save["name_if"].append(Quotation_String_transfor_2(token_list[index]["token"].group().lower()))
        selector_save["type_if"].append("minecraft:player")
        selector_save["limit"] = 1
    elif token_list[index]["type"] == "Selector" :
        Selector_Var = token_list[index]["token"].group()
        if Selector_Var == "@p" :
            selector_save["type_if"].append("minecraft:player")
            selector_save["limit"] = 1
            is_player = True
        elif Selector_Var == "@a" :
            selector_save["type_if"].append("minecraft:player")
            selector_save["is_alive"] = False
            is_player = True
        elif Selector_Var == "@r" :
            selector_save["limit"] = 1
            selector_save["type_if"].append("minecraft:player")
            selector_save["sort"] = "random"
        elif Selector_Var == "@e" : pass
        elif Selector_Var == "@s" :
            selector_save["is_alive"] = False
            selector_save["is_executer"] = True
            selector_save["limit"] = 1
            if is_player and "minecraft:player" not in selector_save["type_if"] : 
                selector_save["type_if"].append("minecraft:player")
            if is_npc and "minecraft:npc" not in selector_save["type_if"] : 
                selector_save["type_if"].append("minecraft:npc")


    if (index+1) < token_list.__len__() and token_list[index+1]["type"] == "Start_Selector_Argument" :
        index += 1
        while token_list[index]["type"] != "End_Selector_Argument" :
            index += 1
            if token_list[index]["type"] == "Next_Selector_Argument" : continue
            if token_list[index]["type"] == "Selector_Argument" : 
                selector_argument_token = token_list[index]["token"]
                selector_argument = selector_argument_token.group()
                selector_argument_count[selector_argument] += 1
                if any( [selector_argument_count[i] > 1 for i in selector_argument_single] ) :
                    raise CompileError("重复的选择器 %s 参数" % selector_argument, 
                    pos=(selector_argument_token.start(),selector_argument_token.end()))
                index = Selector_Save_Set(game_tread, selector_save, token_list, index)
    end_index_save = token_list[-1]["token"].end()

    if is_single and selector_save["limit"] > 1 : raise CompileError("选择器无法选择多个实体", pos=(start_index_save, end_index_save))
    if is_player and (len(selector_save["type_if"]) != 1 or selector_save["type_if"][0] != "minecraft:player") : raise CompileError("选择器只能为玩家类型", pos=(start_index_save, end_index_save))
    if is_npc and (len(selector_save["type_if"]) != 1 or selector_save["type_if"][0] != "minecraft:npc") : raise CompileError("选择器只能为NPC类型", pos=(start_index_save, end_index_save))
    if selector_save["distance"] and selector_save["distance"][0] > selector_save["distance"][1] : raise CompileError("距离参数上限不能小于下限", pos=(start_index_save, end_index_save))
    if selector_save["level"] and selector_save["level"][0] > selector_save["level"][1] : raise CompileError("等级参数上限不能小于下限", pos=(start_index_save, end_index_save))
    if len(selector_save["name_if"]) > 1 : raise CompileError("选择器参数 name 具有重复指定的正选条件", pos=(start_index_save, end_index_save))
    if len(selector_save["name_if"]) > 0 and len(selector_save["name_unless"]) > 0 : raise CompileError("选择器参数 name 同时存在正反选条件", pos=(start_index_save, end_index_save))
    if len(selector_save["type_if"]) > 1 : raise CompileError("选择器参数 type 具有重复指定的正选条件", pos=(start_index_save, end_index_save))
    if len(selector_save["type_if"]) > 0 and len(selector_save["type_unless"]) > 0 : raise CompileError("选择器参数 type 同时存在正反选条件", pos=(start_index_save, end_index_save))
    if len(selector_save["m_if"]) > 1 : raise CompileError("选择器参数 m 具有重复指定的正选条件", pos=(start_index_save, end_index_save))
    if len(selector_save["m_if"]) > 0 and len(selector_save["m_unless"]) > 0 : raise CompileError("选择器参数 m 同时存在正反选条件", pos=(start_index_save, end_index_save))

    return (index+1, functools.partial(RunTime_Selector,game_tread=game_tread,selector_var=selector_save))





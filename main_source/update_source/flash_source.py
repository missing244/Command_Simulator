import zipfile,tarfile,os,re,json,traceback
import package.file_operation as FileOperation
from typing import List,Dict,Union,Literal
source_unzip_dir = os.path.join("main_source", "update_source")
path_split = os.path.join("a","")[1]

def read_json(json:dict,key_list:List[str]) :
    for key1 in key_list : 
        if key1 not in json : return None
        json = json[key1]
    return json

class bedrock_id_info :
    
    damage_item = {
        "leather_helmet":55,"leather_chestplate":80,"leather_leggings":75,"leather_boots":65,"turtle_helmet":275,
        "chainmail_helmet":165,"chainmail_chestplate":240,"chainmail_leggings":225,"chainmail_boots":195,
        "iron_helmet":165,"iron_chestplate":240,"iron_leggings":225,"iron_boots":195,
        "diamond_helmet":363,"diamond_chestplate":528,"diamond_leggings":495,"diamond_boots":429,
        "golden_helmet":77,"golden_chestplate":112,"golden_leggings":105,"golden_boots":91,
        "gnetherite_helmet":407,"netherite_chestplate":592,"netherite_leggings":555,"netherite_boots":481,
        "shears":238,"flint_and_steel":64,"fishing_rod":384,"bow":384,"elytra":432,"crossbow":464,"carrot_on_a_stick":26,
        "warped_fungus_on_a_stick":100,"shield":337,"trident":250,
        "wooden_sword":59,"stone_sword":131,"iron_sword":250,"diamond_sword":1561,"golden_sword":32,"netherite_sword":2031,
        "wooden_axe":59,"stone_axe":131,"iron_axe":250,"diamond_axe":1561,"golden_axe":32,"netherite_axe":2031,
        "wooden_pickaxe":59,"stone_pickaxe":131,"iron_pickaxe":250,"diamond_pickaxe":1561,"golden_pickaxe":32,"netherite_pickaxe":2031,
        "wooden_shovel":59,"stone_shovel":131,"iron_shovel":250,"diamond_shovel":1561,"golden_shovel":32,"netherite_shovel":2031,
        "wooden_hoe":59,"stone_hoe":131,"iron_hoe":250,"diamond_hoe":1561,"golden_hoe":32,"netherite_hoe":2031,"mace":500
    }
    
    enchant_item = {
        "aqua_affinity":["leather_helmet","turtle_helmet","chainmail_helmet","iron_helmet","diamond_helmet","golden_helmet","gnetherite_helmet"],
        "bane_of_arthropods":["wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword","wooden_axe",
            "stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe"],
        "blast_protection":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots"],
        "channeling":["trident"],
        "binding":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots","elytra",
            "carved_pumpkin","skull"],
        "vanishing":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots","elytra",
            "carved_pumpkin","skull","wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword",
            "wooden_axe","stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe","wooden_pickaxe","stone_pickaxe",
            "iron_pickaxe","diamond_pickaxe","golden_pickaxe","netherite_pickaxe","wooden_shovel","stone_shovel","iron_shovel",
            "diamond_shovel","golden_shovel","netherite_shovel","wooden_hoe","stone_hoe","iron_hoe","diamond_hoe","golden_hoe",
            "netherite_hoe","bow","crossbow","fishing_rod","carrot_on_a_stick","warped_fungus_on_a_stick","shears","flint_and_steel",
            "shield","trident","compass","lodestone_compass"],
        "depth_strider":["leather_boots","chainmail_boots","iron_boots","diamond_boots","golden_boots","netherite_boots"],
        "efficiency":["wooden_axe","stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe","wooden_pickaxe","stone_pickaxe",
            "iron_pickaxe","diamond_pickaxe","golden_pickaxe","netherite_pickaxe","wooden_shovel","stone_shovel","iron_shovel",
            "diamond_shovel","golden_shovel","netherite_shovel","wooden_hoe","stone_hoe","iron_hoe","diamond_hoe","golden_hoe",
            "netherite_hoe","shears"],
        "feather_falling":["leather_boots","chainmail_boots","iron_boots","diamond_boots","golden_boots","netherite_boots"],
        "fire_aspect":["wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword",],
        "fire_protection":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots"],
        "flame":["bow"],
        "fortune":["wooden_axe","stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe","wooden_pickaxe","stone_pickaxe",
            "iron_pickaxe","diamond_pickaxe","golden_pickaxe","netherite_pickaxe","wooden_shovel","stone_shovel","iron_shovel",
            "diamond_shovel","golden_shovel","netherite_shovel","wooden_hoe","stone_hoe","iron_hoe","diamond_hoe","golden_hoe",
            "netherite_hoe"],
        "frost_walker":["leather_boots","chainmail_boots","iron_boots","diamond_boots","golden_boots","netherite_boots"],
        "impaling":["trident"],
        "infinity":["bow"],
        "knockback":["wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword"],
        "looting":["wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword"],
        "loyalty":["trident"],
        "luck_of_the_sea":["fishing_rod"],
        "lure":["fishing_rod"],
        "mending":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots","elytra",
            "wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword","wooden_axe","stone_axe",
            "iron_axe","diamond_axe","golden_axe","netherite_axe","wooden_pickaxe","stone_pickaxe","iron_pickaxe","diamond_pickaxe",
            "golden_pickaxe","netherite_pickaxe","wooden_shovel","stone_shovel","iron_shovel","diamond_shovel","golden_shovel",
            "netherite_shovel","wooden_hoe","stone_hoe","iron_hoe","diamond_hoe","golden_hoe","netherite_hoe","bow","crossbow",
            "fishing_rod","carrot_on_a_stick","warped_fungus_on_a_stick","shears","flint_and_steel","shield","trident"],
        "multishot":["crossbow"],
        "piercing":["crossbow"],
        "power":["bow"],
        "projectile_protection":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots"],
            "protection":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots"],
        "punch":["bow"],
        "quick_charge":["crossbow"],
        "respiration":["leather_helmet","turtle_helmet","chainmail_helmet","iron_helmet","diamond_helmet","golden_helmet","gnetherite_helmet"],
        "riptide":["trident"],
        "sharpness":["wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword",
            "wooden_axe","stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe"],
        "silk_touch":["wooden_axe","stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe","wooden_pickaxe","stone_pickaxe",
            "iron_pickaxe","diamond_pickaxe","golden_pickaxe","netherite_pickaxe","wooden_shovel","stone_shovel","iron_shovel",
            "diamond_shovel","golden_shovel","netherite_shovel","wooden_hoe","stone_hoe","iron_hoe","diamond_hoe","golden_hoe",
            "netherite_hoe","shears"],
        "smite":["wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword",
            "wooden_axe","stone_axe","iron_axe","diamond_axe","golden_axe","netherite_axe"],
        "soul_speed":["leather_boots","chainmail_boots","iron_boots","diamond_boots","golden_boots","netherite_boots"],
        "swift_sneak":["leather_leggings","chainmail_leggings","iron_leggings","diamond_leggings","golden_leggings","netherite_leggings"],
        "thorns":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots"],
        "unbreaking":["leather_helmet","leather_chestplate","leather_leggings","leather_boots","turtle_helmet","chainmail_helmet",
            "chainmail_chestplate","chainmail_leggings","chainmail_boots","iron_helmet","iron_chestplate","iron_leggings","iron_boots",
            "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots","golden_helmet","golden_chestplate",
            "golden_leggings","golden_boots","gnetherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots","elytra"
            "wooden_sword","stone_sword","iron_sword","diamond_sword","golden_sword","netherite_sword","wooden_axe","stone_axe",
            "iron_axe","diamond_axe","golden_axe","netherite_axe","wooden_pickaxe","stone_pickaxe","iron_pickaxe","diamond_pickaxe",
            "golden_pickaxe","netherite_pickaxe","wooden_shovel","stone_shovel","iron_shovel","diamond_shovel","golden_shovel",
            "netherite_shovel","wooden_hoe","stone_hoe","iron_hoe","diamond_hoe","golden_hoe","netherite_hoe","bow","crossbow",
            "fishing_rod","carrot_on_a_stick","warped_fungus_on_a_stick","shears","flint_and_steel","shield","trident"],
        "wind_burst":["mace"], "density":["mace"], "breach":["mace"]}
    
    enchant_max_value = {
        "aqua_affinity":1,"bane_of_arthropods":5,"blast_protection":4,"channeling":1,"binding":1,"vanishing":1,"depth_strider":3,
        "efficiency":5,"feather_falling":4,"fire_aspect":2,"fire_protection":4,"flame":1,"fortune":3,"frost_walker":2,
        "impaling":5,"infinity":1,"knockback":2,"looting":3,"loyalty":3,"luck_of_the_sea":3,"lure":3,
        "mending":1,"multishot":1,"piercing":4,"power":5,"projectile_protection":4,"protection":4,"punch":2,"quick_charge":3,
        "respiration":3,"riptide":3,"sharpness":5,"silk_touch":1,"smite":5,"soul_speed":3,"swift_sneak":3,"thorns":3,"unbreaking":3
    }

    dimension = {
        "overworld":{
            "structure" : ["minecraft:ruined_portal"],
            "biome": []
        },
        "nether": {
            "structure" : ["minecraft:bastion_remnant","minecraft:fortress","minecraft:ruined_portal"],
            "biome": ["minecraft:hell","minecraft:soulsand_valley","minecraft:crimson_forest",
                      "minecraft:warped_forest","minecraft:basalt_deltas"]
        },
        "the_end": {
            "structure" : ["minecraft:end_city"],
            "biome": ["minecraft:the_end"]
        }
    }

    tick_damage = ["suicide","override"]

    def get_item_damage(self,item_name:str) :
        if item_name in self.damage_item : return self.damage_item[item_name]
        return None

    def get_item_can_enchant(self,item_name:str) :
        return [i for i in self.enchant_item if (item_name in self.enchant_item[i])]

    def get_enchant_level_max(self,enchant_name:str) :
        if enchant_name in self.enchant_max_value : return self.enchant_max_value[enchant_name]
        return None

    def dimension_of_biome(self,biome_name:str):
        list1 = []
        if biome_name in self.dimension["nether"]["biome"] : list1.append("nether")
        if biome_name in self.dimension["the_end"]["biome"] : list1.append("the_end")
        if len(list1) == 0 or biome_name in self.dimension["overworld"]["biome"] : list1.append("overworld")
        return list1

    def dimension_of_structure(self,structure_name:str):
        list1 = []
        if structure_name in self.dimension["nether"]["structure"] : list1.append("nether")
        if structure_name in self.dimension["the_end"]["structure"] : list1.append("the_end")
        if len(list1) == 0 or structure_name in self.dimension["overworld"]["structure"] : list1.append("overworld")
        return list1

    def can_tick_damage(self,damage_name) :
        if damage_name in self.tick_damage : return True
        return False

bedrock_id_operation = bedrock_id_info()



def unzip_id_file() -> bool :
    zip_path = os.path.join(source_unzip_dir, "minecraft_id.zip")
    if not FileOperation.is_file(zip_path) : raise FileNotFoundError("基岩版ID文件不存在")
    if not zipfile.is_zipfile(zip_path) : raise zipfile.BadZipFile("基岩版ID文件并不是zip压缩包")
    with zipfile.ZipFile(zip_path,"r") as zip_file1 : zip_file1.extractall(os.path.join(source_unzip_dir, "minecraft_id"))
    return True

def unzip_source_file() -> bool :
    tar_path = os.path.join(source_unzip_dir, "be_resource.tar")
    if not FileOperation.is_file(tar_path) : raise FileNotFoundError("基岩版资源文件不存在")
    if not tarfile.is_tarfile(tar_path) : raise tarfile.TarError("基岩版资源文件并不是tar压缩包")
    with tarfile.open(tar_path,"r:bz2") as zip_file1 : zip_file1.extractall(source_unzip_dir)
    return True


def report_source_update_date() -> List[str] :
    info_path = os.path.join(source_unzip_dir,"minecraft_id","_MCBEID_.txt")
    if not FileOperation.is_file(info_path) : raise FileNotFoundError("_MCBEID_.txt 文件不存在")
    text1 = FileOperation.read_a_file(info_path)
    if isinstance(text1,tuple) : raise UnicodeDecodeError("_MCBEID_.txt 文件 utf-8 解码失败")
    text_list = []
    for text in text1.split("\n") :
        if (text[0:4] != "发布时间") and (text[0:6] != "对应游戏版本") : continue
        print(text) ; text_list.append(text)
    return text_list

def read_minecraft_id_files(file_name:str, path:str) -> List[str] :
    if not FileOperation.is_file(path) : raise FileNotFoundError("%s.txt 文件不存在" % file_name)
    text1 = FileOperation.read_a_file(path)
    if isinstance(text1,tuple) : raise UnicodeDecodeError("%s.txt 文件 utf-8 解码失败" % file_name)
    id_match = re.compile("^[a-zA-Z0-9_\\u002e]+\\u003a[a-zA-Z0-9_\\u002e]+|^[a-zA-Z0-9_\\u002e]+")
    return [id_match.match(i).group() for i in text1.split("\n") if id_match.match(i)]

def update_minecraft_id() -> Dict[Literal["success","error"],Union[list,list]] :
    minecraft_id = {
        "item": {
            "need_namespace": True,
            "path": os.path.join(source_unzip_dir,"minecraft_id","item.txt"), 
            "info_data": {"damage_max": bedrock_id_operation.get_item_damage, "can_enchant": bedrock_id_operation.get_item_can_enchant}
        },
        "gamerule": {"path": os.path.join(source_unzip_dir,"minecraft_id","gamerule.txt"), "info_data": {}},
        "block": {"need_namespace": True, "path": os.path.join(source_unzip_dir,"minecraft_id","block.txt"), "info_data": {}},
        "enchant": {
            "path": os.path.join(source_unzip_dir,"minecraft_id","enchant.txt"),
            "info_data": {"max_level": bedrock_id_operation.get_enchant_level_max}
        },
        "biome": {
            "need_namespace": True,
            "path": os.path.join(source_unzip_dir,"minecraft_id","biome.txt"), 
            "info_data": {"dimension":bedrock_id_operation.dimension_of_biome}
        },
        "structure": {
            "need_namespace": True,
            "path": os.path.join(source_unzip_dir,"minecraft_id","location.txt"),
            "info_data": {"dimension": bedrock_id_operation.dimension_of_structure}
        },
        "damageCause": {
            "path": os.path.join(source_unzip_dir,"minecraft_id","damageCause.txt"),
            "info_data": {"modify_in_tick": bedrock_id_operation.can_tick_damage}
        },
        "effect": {"path": os.path.join(source_unzip_dir,"minecraft_id","effect.txt"), "info_data": {}},
        "recipe": {"path": os.path.join(source_unzip_dir,"minecraft_id","recipe.txt"), "info_data": {}},
        "entitySlot": {"path": os.path.join(source_unzip_dir,"minecraft_id","entitySlot.txt"), "info_data": {}},
    }
    logs = {"success":[], "error":[]}
    
    for id_name in minecraft_id :
        result_json = {}
        try : id_list = read_minecraft_id_files(id_name,minecraft_id[id_name]["path"])
        except : logs["error"].append(traceback.format_exc().split("\n")[-2])
        else :
            for name in id_list :
                info_data = minecraft_id[id_name]["info_data"].copy()
                for key in info_data : info_data[key] = info_data[key](name)
                if "need_namespace" in minecraft_id[id_name] and minecraft_id[id_name]["need_namespace"] : 
                    if name[0:10] == "minecraft:" : result_json[name] = info_data
                    else : result_json["minecraft:%s" % name] = info_data
                else : result_json[name] = info_data
            FileOperation.write_a_file(os.path.join(source_unzip_dir,"import_files","%s" % id_name), json.dumps(result_json,indent=2))
            logs["success"].append("文件 %s 成功刷新" % id_name)
    
    return logs

def update_minecraft_source() -> Dict[Literal["success","error"],Union[list,list]] :
    minecraft_source = {
        "animation_controller": {"path": os.path.join(source_unzip_dir,"resource_packs","animation_controllers"), "info_data": {}},
        "animation": {"path": os.path.join(source_unzip_dir,"resource_packs","animations"), "info_data": {}},
        "fog": {"path": os.path.join(source_unzip_dir,"resource_packs","fogs"), "info_data": {}},
        "particle": {"path": os.path.join(source_unzip_dir,"resource_packs","particles"), "info_data": {}},
        "sound": {"path": os.path.join(source_unzip_dir,"resource_packs","sounds"), "info_data": {}},
        "music": {"path": os.path.join(source_unzip_dir,"resource_packs","sounds"),"info_data": {}},
        "loot_table": {"path": os.path.join(source_unzip_dir,"behavior_packs","loot_tables"), "info_data": {}},
        "trading": {"path": os.path.join(source_unzip_dir,"behavior_packs","trading"), "info_data": {}},
        "entity": {"path": os.path.join(source_unzip_dir,"behavior_packs","entities"), "info_data": {}},
    }
    logs = {"success":[], "error":[]}


    for id_name in minecraft_source :
        result_json = {}
        if not FileOperation.is_dir(minecraft_source[id_name]["path"]) : 
            logs["error"].append("%s 文件夹不存在" % id_name) ; continue

        if id_name in ("loot_table", "trading", "entity") :
            file_list = [i for i in FileOperation.file_in_path(minecraft_source[id_name]["path"]) if re.search("\\u002ejson$",i)]
            for file_path in file_list :
                simple_path = "/".join( file_path.replace(os.path.join(source_unzip_dir,"behavior_packs",""),"",1).split(path_split) )
                try : json_obj = json.loads(FileOperation.read_a_file(file_path))
                except : logs["error"].append("文件 %s 加载失败" % simple_path)
                else : 
                    if id_name == "entity" : 
                        value = read_json(json_obj,["minecraft:entity","description"])
                        if not value or ("identifier" not in value) : continue
                        if "is_summonable" not in value : value["is_summonable"] = True
                        if "component_groups" not in json_obj["minecraft:entity"] : 
                            json_obj["minecraft:entity"]["component_groups"] = {}
                        if "components" not in json_obj["minecraft:entity"] : 
                            json_obj["minecraft:entity"]["components"] = {}
                        if "events" not in json_obj["minecraft:entity"] : 
                            json_obj["minecraft:entity"]["events"] = {}
                        result_json[value["identifier"]] = json_obj["minecraft:entity"]
                    else : result_json[simple_path] = json_obj
        else :
            base_path = minecraft_source[id_name]["path"]
            file_list:List[str] = [os.path.join(base_path,i) for i in os.listdir(base_path) if re.search("\\u002ejson$",i)]
            file_list = [i for i in file_list if FileOperation.is_file(i)] 
            for file_path in file_list :
                simple_path = "/".join( file_path.replace(os.path.join(source_unzip_dir,"resource_packs",""),"",1).split(path_split) )
                try : json_obj = json.loads(FileOperation.read_a_file(file_path))
                except : logs["error"].append("文件 %s 加载失败" % simple_path)
                else : 
                    if id_name in ("fog", "particle") :
                        if id_name == "fog" : value = read_json(json_obj,["minecraft:fog_settings","description","identifier"])
                        elif id_name == "particle" : value = read_json(json_obj,["particle_effect","description","identifier"])
                        if value : result_json[value] = {}
                    elif id_name == "animation_controller" : result_json.update({ i:{} for i in read_json(json_obj,["animation_controllers"]) })
                    elif id_name == "animation" : result_json.update({ i:{} for i in read_json(json_obj,["animations"]) })
                    elif id_name == "sound" : result_json.update({ i:{} for i in json_obj })
                    elif id_name == "music" : result_json.update({ i:{} for i in json_obj if re.search("^(record|music\\u002egame)",i) })

        FileOperation.write_a_file(os.path.join(source_unzip_dir,"import_files","%s" % id_name), json.dumps(result_json,indent=2))
        logs["success"].append("文件 %s 成功刷新" % id_name)

    return logs


def flash_search_id() -> Dict[Literal["success","error"],Union[list,list]] :
    open_file_list = {
        "[物品]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'item.txt'), "name": "item"},
        "[方块]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'block.txt'), "name": "block"},
        "[实体]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'entity.txt'), "name": "entity"},
        "[群系]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'biome.txt'), "name": "biome"},
        "[伤害]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'damageCause.txt'), "name": "damageCause"},
        "[药效]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'effect.txt'), "name": "effect"},
        "[附魔]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'enchant.txt'), "name": "enchant"},
        "[槽位]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'entitySlot.txt'), "name": "entitySlot"},
        "[迷雾]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'fog.txt'), "name": "fog"},
        "[规则]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'gamerule.txt'), "name": "gamerule"},
        "[结构]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'location.txt'), "name": "location"},
        "[掉落]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'lootTable.txt'), "name": "lootTable"},
        "[声音]" : {"path": os.path.join(source_unzip_dir,"minecraft_id",'sound.txt'), "name": "sound"}
    }
    
    id_translat = {}
    logs = {"success":[],  "error":[]}

    for id_name in open_file_list :
        if not FileOperation.is_file(open_file_list[id_name]["path"]) :
            logs["error"].append("%s 文件不存在" % open_file_list[id_name]["name"])
            continue
        try : file = open(open_file_list[id_name]["path"], "r", encoding="utf-8")
        except : logs["error"].append("%s 文件utf-8解码失败" % open_file_list[id_name]["name"])
        else :
            content1 = file.read().split("\n")
            content1 = [tuple(text.split(": ",1)) for text in content1[1 : len(content1)-3]]
            id_translat[id_name] = { (text_list[0] if id_name != "[实体]" else text_list[0].replace("minecraft:", "", 1)) :
                text_list[1].replace("（不可召唤）","") for text_list in content1 if (text_list[1] != "")
            }
            file.close()
            logs["success"].append("%s 文件翻译提取成功" % open_file_list[id_name]["name"])
    
    FileOperation.write_a_file(os.path.join(source_unzip_dir,"import_files","translate"), json.dumps(id_translat,ensure_ascii=False))
    return logs



if 0 :
    print(os.path.realpath("."))
    print(unzip_id_file())
    print(unzip_source_file())
    print(report_source_update_date())
    print(update_minecraft_id())
    print(update_minecraft_source())
    print(flash_search_id())


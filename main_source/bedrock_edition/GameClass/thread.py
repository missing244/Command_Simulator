import threading, os, zipfile, json, functools, re, inspect, traceback, time, random, math, sys
from . import jsonc, nbt
from .. import Constants, MCCommandParser, MCStructureManage, np
from pathlib import Path
from typing import List, Dict, Union, Literal, Tuple, TypedDict, Callable, Optional, Type, Protocol, Sequence, Any
HARDCORE_FILE = zipfile.ZipFile(os.path.realpath(os.path.join(__file__, "..", "..", "hardcore.zip")), "r")
CommonStructure = MCStructureManage.CommonStructure
ParserResult = MCCommandParser.ParserResult

if "TypeDefine" :
    class BlockRegisterData(TypedDict) :
        state: Dict[str, Union[bool, int, str]]

    class RunTimeCallback(Protocol):
        def __call__(self, _game:"MinecraftSimulator", *args, **kwargs) :
            ...


class StartupGameSource :

    def __init__(self, main_thread:"MinecraftSimulator") :
        self.main_thread = main_thread
        self.world_path = main_thread.WorldPath
        self.current_root_path = Path.cwd()
        self.RP_folders:Dict[Path, None] = {}
        self.BP_folders:Dict[Path, Optional[Tuple[int, int, int]]] = {}
        self.RP_load_errors:Dict[str, List[str]] = {}
        self.BP_load_errors:Dict[str, List[str]] = {}
        self.RP_read_errors:Dict[str, List[str]] = {}
        self.BP_read_errors:Dict[str, List[str]] = {}

        self.FOG:Dict[str, None] = json.loads(HARDCORE_FILE.read("[RP]fog.json"))
        self.SOUND:Dict[str, None] = json.loads(HARDCORE_FILE.read("[RP]sound.json"))
        self.PARTICLE:Dict[str, None] = json.loads(HARDCORE_FILE.read("[RP]particle.json"))
        self.ANIMATION:Dict[str, None] = json.loads(HARDCORE_FILE.read("[RP]animations.json"))
        self.ANIMATION_CONTROLLER:Dict[str, None] = json.loads(HARDCORE_FILE.read("[RP]animation_controller.json"))

        self.ITEM:Dict[str, Dict] = json.loads(HARDCORE_FILE.read("[BP]item.json"))
        self.BLOCK:Dict[str, Union[None, BlockRegisterData]] = json.loads(HARDCORE_FILE.read("[BP]block.json"))
        self.ENTITY:Dict[str, Dict] = json.loads(HARDCORE_FILE.read("[BP]entity.json"))
        self.RECIPE:Dict[str, None] = json.loads(HARDCORE_FILE.read("[BP]recipe.json"))
        self.LOOT_TABLE:Dict[str, Dict] = json.loads(HARDCORE_FILE.read("[BP]loot_table.json"))
        self.FEATURE:Dict[str, None] = json.loads(HARDCORE_FILE.read("[BP]feature.json"))
        self.FEATURE_RULE:Dict[str, None] = json.loads(HARDCORE_FILE.read("[BP]feature_rule.json"))
        self.CAMERA_PERSET:Dict[str, None] = json.loads(HARDCORE_FILE.read("additional_data.json"))["camera_perset"]

        self.DIALOGUES:Dict[str, None] = {}
        self.AIM_ASSIST:Dict[str, None] = {}
        self.TEMPLATE_POOL:Dict[str, None] = {}
        self.TEMPLATE_STRUCTURE:Dict[str, None] = {}
        self.MCFUNCTIONS:Dict[str, Tuple[str, Tuple[int, int, int], List[str]]] = {}

        if not main_thread.IsChallenge : self.__pack_loader__()

    def __manifest_verify__(self, paths:List[Path]) -> Tuple[List[Path], Dict[str, List[str]]] :

        def validate_uuid(uuid_str: str) -> bool:
            """检查字符串是否为有效的 UUID 格式"""
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            return bool(re.match(pattern, uuid_str, re.IGNORECASE))

        def validate_version_array(version) -> bool:
            """检查版本数组是否为包含三个整数的列表"""
            if not isinstance(version, list) : return False
            if len(version) != 3 : return False
            return all(isinstance(v, int) for v in version)

        success_load:Dict[Path, Optional[Tuple[int, int, int]]] = {}
        errors:Dict[str, List[str]] = {}

        for pack_path in paths :
            manifest_path = pack_path / 'manifest.json'
            pack_root_path = pack_path.absolute().relative_to(self.current_root_path)
            current_error = errors[str(pack_root_path)] = []

            if not manifest_path.is_file() : 
                current_error.append(f"{pack_root_path} 无 manifest.json 文件")
                continue

            # 1. 根字段检查
            try : data = jsonc.JsoncParser.parse_file(manifest_path)
            except : current_error.append(f"{pack_root_path} manifest.json 文件读取失败(编码错误或内容语法错误)") ; continue
            required_root_fields = ["format_version", "header", "modules"]
            for field in required_root_fields :
                if field not in data : current_error.append(f"缺少根字段: {field}")
            if current_error : continue

            # format_version检查
            if not isinstance(data["format_version"], int) : current_error.append("format_version 必须是整数") ; continue
            elif not(1 <= data["format_version"] <= 2) : current_error.append("format_version 应为 1或2") ; continue

            # 2. header 对象检查
            header = data["header"]
            if not isinstance(header, dict) : current_error.append("header 必须是一个对象") ; continue

            required_header_fields = ["description", "name", "uuid", "version"]
            for field in required_header_fields :
                if field not in header : current_error.append(f"header 中缺少字段: {field}")

            if "description" in header and not isinstance(header["description"], str):
                current_error.append("header.description 必须是字符串")
            if "name" in header and not isinstance(header["name"], str):
                current_error.append("header.name 必须是字符串")
            if "uuid" in header and (not isinstance(header["uuid"], str) or not validate_uuid(header["uuid"])):
                current_error.append(f"header.uuid 不是有效的 UUID: {header.get('uuid')}")
            if "version" in header and not validate_version_array(header["version"]):
                current_error.append("header.version 必须是包含三个整数的数组 (例如 [1,0,0])")
            if "min_engine_version" in header and not validate_version_array(header["min_engine_version"]):
                current_error.append("header.min_engine_version 必须是包含三个整数的数组")

            if not current_error : 
                if "min_engine_version" not in header : success_load[pack_path] = self.main_thread.GameVersion
                else : success_load[pack_path] = tuple(header["min_engine_version"])[0:3]

        return success_load, errors

    def __pack_loader__(self):
        RP_root_path = self.world_path / 'resource_packs'
        if RP_root_path.is_dir() : self.RP_folders = [p for p in RP_root_path.iterdir() if p.is_dir()]
        BP_root_path = self.world_path / 'behavior_packs'
        if BP_root_path.is_dir() : self.BP_folders = [p for p in BP_root_path.iterdir() if p.is_dir()]
        self.RP_folders, self.RP_load_errors = self.__manifest_verify__(self.RP_folders)
        self.BP_folders, self.BP_load_errors = self.__manifest_verify__(self.BP_folders)


    def update_RP_animations(self) :
        for RP_path in self.RP_folders :
            target_path = RP_path / 'animations'
            pack_root_path = RP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.RP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("animation错误(JsonParserError)：%s" % file_path)
                else : 
                    if not isinstance(content, dict): ErrorAppend("animation错误(JsonRootTypeError)：%s" % file_path)
                    else: self.ANIMATION.update( (i, None) for i in content.keys() )

    def update_RP_controllers(self) :
        for RP_path in self.RP_folders :
            target_path = RP_path / 'animation_controllers'
            pack_root_path = RP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.RP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("animation_controller错误(JsonParserError)：%s" % file_path)
                else : 
                    if not isinstance(content, dict): ErrorAppend("animation_controller错误(JsonRootTypeError)：%s" % file_path)
                    else: self.ANIMATION_CONTROLLER.update( (i, None) for i in content.keys() )

    def update_RP_fogs(self) :
        for RP_path in self.RP_folders :
            target_path = RP_path / 'fogs'
            pack_root_path = RP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.RP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("fog错误(JsonParserError)：%s" % file_path) ; continue
                try : k = content['minecraft:fog_settings']['description']['identifier']
                except : ErrorAppend("fog错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(k, str) and ":" in k : self.FOG[k] = None
                else : ErrorAppend("fog错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_RP_particles(self) :
        for RP_path in self.RP_folders :
            target_path = RP_path / 'particles'
            pack_root_path = RP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.RP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("particle错误(JsonParserError)：%s" % file_path) ; continue
                try : k = content['particle_effect']['description']['identifier']
                except : ErrorAppend("particle错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(k, str) and ":" in k : self.PARTICLE[k] = None
                else : ErrorAppend("particle错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_RP_sounds(self) :
        for RP_path in self.RP_folders :
            file_path = RP_path / 'sounds' / 'sound_definitions.json'
            pack_root_path = RP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.RP_read_errors.setdefault(str(pack_root_path), []).append

            if not file_path.is_file() : continue
            try : content = jsonc.JsoncParser.parse_file(file_path)
            except : ErrorAppend("sound错误(JsonParserError)：%s" % file_path)
            else : 
                if not isinstance(content, dict): ErrorAppend("sound错误(JsonRootTypeError)：%s" % file_path)
                else: self.SOUND.update( (i, None) for i in content.keys() )

    def update_BP_blocks(self) :

        def validate_state_value(data:Union[list, dict]) -> bool:
            """
            验证输入格式是否符合预期。

            规则：
            - 如果是列表：
                - 所有元素类型必须相同，且只能是 str、bool 或 int 中的一种。
            - 如果是字典：
                - 必须只包含一个键 "values"。
                - "values" 的值必须是一个字典，且仅包含键 "min" 和 "max"。
                - "min" 和 "max" 的值必须是整数（int）。
            - 其他情况返回 False。
            """
            # 处理列表
            if isinstance(data, list):
                if not data : return False # 不允许空列表
                first_type = type(data[0]) # 获取第一个元素的真实类型（注意 bool 是 int 的子类，需严格区分）
                allowed_types = (str, bool, int)
                if first_type not in allowed_types : return False
                return all(type(item) is first_type for item in data) # 检查所有元素类型是否与第一个元素相同

            # 处理字典
            if isinstance(data, dict) :
                if "values" not in data : return False   # 根字典有一个键 "values"
                values_dict = data["values"]
                if not isinstance(values_dict, dict) : return False  # values_dict 必须是字典
                if "min" not in values_dict or "max" not in values_dict  : return False # values_dict 只能包含 "min" 和 "max"
                if not isinstance(values_dict["min"], int) or not isinstance(values_dict["max"], int) : return False
                return True

            # 其他类型
            return False

        for BP_path in self.BP_folders :
            target_path = BP_path / 'blocks'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("block错误(JsonParserError)：%s" % file_path) ; continue
                try : block_id = content['minecraft:block']['description']['identifier']
                except : ErrorAppend("block错误(JsonKeyPathError)：%s" % file_path) ; continue

                if not isinstance(block_id, str) or ":" not in block_id : 
                    ErrorAppend("block错误(IdentifierNameError)：%s" % file_path) ; continue
                block_state = content['minecraft:block']['description'].get("states", {})
                if not isinstance(block_state, dict) : ErrorAppend("block错误(StateDefineError)：%s" % file_path) ; continue
                ErrorTest = [k for k, v in block_state.items() if not validate_state_value(v)]
                if ErrorTest : ErrorAppend("block错误(StateValueError)：%s" % file_path) ; continue
                
                block_components = content['minecraft:block'].get("components", {})
                if not isinstance(block_components, dict) : ErrorAppend("block错误(ComponentDefineError)：%s" % file_path) ; continue
                block_loot = block_components.get("minecraft:loot")
                if not block_loot or not block_state : self.BLOCK[block_id] = None
                else : self.BLOCK[block_id] = {"block_state": block_state, "block_loot":block_loot}

    def update_BP_items(self) :
        valid_slots = {"slot.armor.chest", "slot.armor.feet", "slot.armor.legs"}
        valid_enchat = {
        'g_armor': ['soul_speed', 'mending', 'aqua_affinity', 'feather_falling', 'depth_strider', 
            'blast_protection', 'swift_sneak', 'frost_walker', 'fire_protection', 'protection', 
            'thorns', 'projectile_protection', 'respiration', 'vanishing', 'unbreaking', 'binding'], 
        'g_tool': ['sharpness', 'smite', 'bane_of_arthropods', 'efficiency', 'silk_touch', 'unbreaking', 'fortune', 'mending', 'vanishing'], 
        'g_digging': ['efficiency', 'silk_touch', 'unbreaking', 'fortune', 'mending', 'vanishing'], 
        'armor_head': ["protection", "fire_protection", "blast_protection", "projectile_protection","thorns", 
            "respiration", "aqua_affinity", "unbreaking", "mending", "binding", "vanishing"], 
        'armor_torso': ['protection', 'fire_protection', 'blast_protection', 'projectile_protection', 'thorns', 
            'unbreaking', 'mending', 'binding', 'vanishing'], 
        'armor_feet': ['protection', 'fire_protection', 'feather_falling', 'blast_protection', 'projectile_protection', 
            'thorns', 'depth_strider', 'unbreaking', 'frost_walker', 'mending', 'binding', 'vanishing', 'soul_speed'], 
        'armor_legs': ['protection', 'fire_protection', 'blast_protection', 'projectile_protection', 'thorns', 
            'unbreaking', 'mending', 'binding', 'vanishing', 'swift_sneak'], 
        'sword': ['sharpness', 'smite', 'bane_of_arthropods', 'knockback', 'fire_aspect', 'looting', 'unbreaking', 'mending', 'vanishing'], 
        'bow': ['unbreaking', 'power', 'punch', 'flame', 'infinity', 'mending', 'vanishing'],
        'spear': ['sharpness', 'smite', 'bane_of_arthropods', 'knockback', 'fire_aspect', 'looting', 'unbreaking', 'mending', 'vanishing', 'lunge'], 
        'crossbow': ['unbreaking', 'mending', 'vanishing', 'multishot', 'piercing', 'quick_charge'], 
        'melee_spear': ['unbreaking', 'mending', 'vanishing', 'impaling', 'riptide', 'loyalty', 'channeling'], 
        'hoe': ['efficiency', 'silk_touch', 'unbreaking', 'fortune', 'mending', 'vanishing'], 
        'shears': ['efficiency', 'silk_touch', 'unbreaking', 'mending', 'vanishing'], 
        'flintsteel': ["unbreaking", "mending", "vanishing"], 
        'shield': ["unbreaking", "mending", "vanishing"], 
        'axe': ['sharpness', 'smite', 'bane_of_arthropods', 'efficiency', 'silk_touch', 'unbreaking', 'fortune', 'mending', 'vanishing'], 
        'pickaxe': ['efficiency', 'silk_touch', 'unbreaking', 'fortune', 'mending', 'vanishing'], 
        'shovel': ['efficiency', 'silk_touch', 'unbreaking', 'fortune', 'mending', 'vanishing'], 
        'fishing_rod': ['unbreaking', 'luck_of_the_sea', 'lure', 'mending', 'vanishing'], 
        'carrot_stick': ["unbreaking", "mending", "vanishing"], 
        'elytra': ['unbreaking', 'mending', 'binding', 'vanishing'], 
        'cosmetic_head': ["binding", "vanishing"]}
        all_enchant = list(json.loads(HARDCORE_FILE.read("[SV]enchant.json")).keys())
        for BP_path in self.BP_folders :
            target_path = BP_path / 'items'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("item错误(JsonParserError)：%s" % file_path) ; continue
                try : item_id = content['minecraft:item']['description']['identifier']
                except : ErrorAppend("item错误(JsonKeyPathError)：%s" % file_path) ; continue

                if not isinstance(item_id, str) or ":" not in item_id : 
                    ErrorAppend("item错误(IdentifierNameError)：%s" % file_path) ; continue
                else : self.ITEM[item_id] = {}

                try : max_durability = content["minecraft:item"]["components"]["minecraft:durability"]["max_durability"]
                except : pass
                else : 
                    if not isinstance(max_durability, int): ErrorAppend("item错误(DurabilityTypeError)：%s" % file_path)
                    elif not(1 <= max_durability <= 32767) : ErrorAppend("item错误(DurabilityValueError)：%s" % file_path)
                    else : self.ITEM[item_id]["damage"] = max_durability
                try : max_stack_size = content["minecraft:item"]["components"]["minecraft:max_stack_size"]
                except : pass
                else : 
                    if not isinstance(max_stack_size, int): ErrorAppend("item错误(StackTypeError)：%s" % file_path)
                    elif not(1 <= max_stack_size <= 64) : ErrorAppend("item错误(StackValueError)：%s" % file_path)
                    else : self.ITEM[item_id]["max_count"] = max_stack_size

                try: wearable = content["minecraft:item"]["components"]["minecraft:wearable"]
                except : pass
                else :
                    slot = wearable.get("slot") if isinstance(wearable, dict) else None
                    if slot in valid_slots: self.ITEM[item_id]["wear_slot"] = slot

                try: enchantable = content["minecraft:item"]["components"]["minecraft:enchantable"]
                except : pass
                else :
                    slot = enchantable.get("slot") if isinstance(enchantable, dict) else None
                    if slot == "none" : pass
                    elif slot == "all" : self.ITEM[item_id]["can_enchant"] = all_enchant.copy()
                    elif slot in valid_enchat: self.ITEM[item_id]["can_enchant"] = valid_enchat[slot].copy()

    def update_BP_entities(self) :
        for BP_path in self.BP_folders :
            target_path = BP_path / 'entities'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("entity错误(JsonParserError)：%s" % file_path) ; continue
                try : entity_id = content['minecraft:entity']['description']['identifier']
                except : ErrorAppend("entity错误(JsonKeyPathError)：%s" % file_path) ; continue
                
                entity_data = content.get("minecraft:entity", {})
                if not isinstance(entity_data.get("events", None), dict) : entity_data["events"] = {}
                if not isinstance(entity_data.get("components", None), dict) : entity_data["components"] = {}
                if not isinstance(entity_data.get("component_groups", None), dict) : entity_data["component_groups"] = {}
                if entity_id in self.ENTITY : 
                    for i in {"events", "components", "component_groups"} :
                        for k,v in entity_data[i].items() : self.ENTITY[entity_id][k] = v
                else : self.ENTITY[entity_id] = entity_data

    def update_BP_recipes(self) :
        recipe_types = ["minecraft:recipe_brewing_mix", "minecraft:recipe_furnace", "minecraft:recipe_shaped", 
            "minecraft:recipe_shapeless", "minecraft:recipe_smithing_transform", "minecraft:recipe_smithing_trim"]
        for BP_path in self.BP_folders :
            target_path = BP_path / 'recipes'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("recipe错误(JsonParserError)：%s" % file_path) ; continue

                recipe_id = None
                for recipe_type in recipe_types :
                    try : recipe_id = content[recipe_type]['description']['identifier']
                    except : continue
                    else : break
                if recipe_id is None : ErrorAppend("recipe错误(JsonKeyPathError)：%s" % file_path) ; continue
                if not isinstance(recipe_id, str) : ErrorAppend("recipe错误(IdentifierNameError)：%s" % file_path)
                else : self.RECIPE[recipe_id] = None

    def update_BP_cameras(self) :
        for BP_path in self.BP_folders :
            target_path = BP_path / 'cameras'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("camera错误(JsonParserError)：%s" % file_path) ; continue
                try : k = content['minecraft:camera_preset']['identifier']
                except : ErrorAppend("camera错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(k, str) and ":" in k : self.CAMERA_PERSET[k] = None
                else : ErrorAppend("camera错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_BP_dialogue(self) :
        for BP_path in self.BP_folders :
            target_path = BP_path / 'dialogue'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("dialogue错误(JsonParserError)：%s" % file_path) ; continue
                try : scenes_list = content['minecraft:npc_dialogue']['scenes']
                except : ErrorAppend("dialogue错误(JsonKeyPathError)：%s" % file_path) ; continue

                if not isinstance(scenes_list, list) : ErrorAppend("dialogue错误(SceneDefineTypeError)：%s" % file_path) ; continue
                for scenes in scenes_list :
                    if not isinstance(scenes, dict) : continue
                    scene_name = scenes.get("scene_tag")
                    if scene_name is None : ErrorAppend("dialogue错误(SceneNameUndefindError)：%s" % file_path) ; continue
                    if not isinstance(scene_name, str) : ErrorAppend("dialogue错误(SceneNameError)：%s" % file_path) ; continue
                    self.DIALOGUES[scene_name] = None

    def update_BP_loots(self) :
        
        def validate_loot_table_manual(data: dict) -> bool:
            if "pools" not in data: raise ValueError("缺少 'pools' 字段")
            if not isinstance(data["pools"], list): raise ValueError("'pools' 必须是数组")
            for idx, pool in enumerate(data["pools"]): _validate_pool(pool, f"pools[{idx}]")
            return True

        def _validate_pool(pool: dict, path: str):
            if not isinstance(pool, dict): raise ValueError(f"{path} 必须是对象")
            if "rolls" not in pool: raise ValueError(f"{path} 缺少 'rolls'")
            if "entries" not in pool: raise ValueError(f"{path} 缺少 'entries'")

            # 验证 rolls 类型
            rolls = pool["rolls"]
            if isinstance(rolls, (int, float)):
                if rolls < 0: raise ValueError(f"{path}.rolls 不能为负数")
            elif isinstance(rolls, dict):
                if "min" not in rolls or "max" not in rolls:
                    raise ValueError(f"{path}.rolls 对象必须包含 'min' 和 'max'")
                if not isinstance(rolls["min"], int) or not isinstance(rolls["max"], int):
                    raise ValueError(f"{path}.rolls.min/max 必须为整数")
                if rolls["min"] < 0 or rolls["max"] < 0:
                    raise ValueError(f"{path}.rolls.min/max 不能为负数")
            else: raise ValueError(f"{path}.rolls 类型错误：仅支持整数或对象")

            # 验证 entries
            if not isinstance(pool["entries"], list):
                raise ValueError(f"{path}.entries 必须是数组")
            for e_idx, entry in enumerate(pool["entries"]):
                _validate_entry(entry, f"{path}.entries[{e_idx}]")

        def _validate_entry(entry: dict, path: str):
            if not isinstance(entry, dict): raise ValueError(f"{path} 必须是对象")
            if "type" not in entry: raise ValueError(f"{path} 缺少 'type'")
            etype, eweight = entry["type"], entry.get("weight", 1)
            if etype not in {"item", "loot_table", "empty"}:
                raise ValueError(f"{path}.type 值无效: {etype}")

            if etype in {"item", "loot_table"}:
                if "name" not in entry: raise ValueError(f"{path} 缺少 'name'（因为 type={etype}）")
                if not isinstance(entry["name"], str): raise ValueError(f"{path}.name 必须是字符串")

            if not isinstance(eweight, int): raise ValueError(f"{path}.weight 必须是整数")

            if "functions" in entry:
                if not isinstance(entry["functions"], list): raise ValueError(f"{path}.functions 必须是数组")
                for f_idx, func in enumerate(entry["functions"]):
                    if not isinstance(func, dict) or "function" not in func:
                        raise ValueError(f"{path}.functions[{f_idx}] 缺少 'function' 或不是对象")

        for BP_path in self.BP_folders :
            target_path = BP_path / 'loot_tables'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.rglob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("loot_table错误(JsonParserError)：%s" % file_path) ; continue
                if not isinstance(content, dict) : ErrorAppend("loot_table错误(JsonTypeError)：%s" % file_path) ; continue
                try : validate_loot_table_manual(content)
                except Exception as e : ErrorAppend("loot_table错误(ContentError)：%s(%s)" % (file_path, e.args[0])) ; continue

                name = str(file_path.relative_to(target_path)).replace("\\", "/")
                self.LOOT_TABLE[name] = content

    def update_BP_features(self) :
        feature_types = [
            "minecraft:aggregate_feature", "minecraft:cave_carver_feature", "minecraft:fossil_feature",
            "minecraft:geode_feature", "minecraft:growing_plant_feature", "minecraft:height_difference_filter_feature",
            "minecraft:multiface_feature", "minecraft:nether_cave_carver_feature", "minecraft:ore_feature",
            "minecraft:partially_exposed_blob_feature", "minecraft:scatter_feature", "minecraft:search_feature",
            "minecraft:sequence_feature", "minecraft:single_block_feature", "minecraft:snap_to_surface_feature",
            "minecraft:structure_template_feature", "minecraft:surface_relative_threshold_feature",
            "minecraft:tree_feature", "minecraft:underwater_cave_carver_feature", "minecraft:vegetation_patch_feature",
            "minecraft:weighted_random_feature"]
        for BP_path in self.BP_folders :
            target_path = BP_path / 'features'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("feature错误(JsonParserError)：%s" % file_path) ; continue

                feature_id = None
                for feature_type in feature_types :
                    try : feature_id = content[feature_type]["description"]['identifier']
                    except : continue
                    else : break
                if feature_id is None : ErrorAppend("feature错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(feature_id, str) : self.FEATURE[feature_id] = None
                else : ErrorAppend("feature错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_BP_feature_rules(self) :
        for BP_path in self.BP_folders :
            target_path = BP_path / 'feature_rules'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("feature_rule错误(JsonParserError)：%s" % file_path) ; continue
                try : k = content["minecraft:feature_rules"]["description"]['identifier']
                except : ErrorAppend("feature_rule错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(k, str) : self.FEATURE_RULE[k] = None
                else : ErrorAppend("feature_rule错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_BP_template_pools(self) :
        for BP_path in self.BP_folders :
            target_path = BP_path / 'worldgen' / 'template_pools'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("template_pool错误(JsonParserError)：%s" % file_path) ; continue
                try : k = content["minecraft:template_pool"]["description"]['identifier']
                except : ErrorAppend("template_pool错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(k, str) and ":" in k : self.TEMPLATE_POOL[k] = None
                else : ErrorAppend("template_pool错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_BP_template_structures(self) :
        for BP_path in self.BP_folders :
            target_path = BP_path / 'worldgen' / 'structures'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = self.BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.glob("*.json") :
                if not file_path.is_file() : continue
                try : content = jsonc.JsoncParser.parse_file(file_path)
                except : ErrorAppend("template_structure错误(JsonParserError)：%s" % file_path) ; continue
                try : k = content["minecraft:jigsaw"]["description"]['identifier']
                except : ErrorAppend("template_structure错误(JsonKeyPathError)：%s" % file_path) ; continue
                if isinstance(k, str) and ":" in k : self.TEMPLATE_STRUCTURE[k] = None
                else : ErrorAppend("template_structure错误(IdentifierNameError)：%s" % file_path) ; continue

    def update_BP_mcfunction(self) :
        BP_read_errors: Dict[str, List[str]] = {}
        for BP_path in self.BP_folders :
            target_path = BP_path / 'functions'
            pack_root_path = BP_path.absolute().relative_to(self.current_root_path)
            ErrorAppend = BP_read_errors.setdefault(str(pack_root_path), []).append

            for file_path in target_path.rglob("*.mcfunction") :
                if not file_path.is_file() : continue
                try : content = open(file_path, "r", encoding="utf-8").read().split("\n")
                except : ErrorAppend("functions错误(TextDecodeError)：%s" % file_path) ; continue

                name = str(file_path.relative_to(target_path)).replace("\\", "/")
                self.MCFUNCTIONS[name] = (str(file_path), self.BP_folders.get(BP_path), content)
        return BP_read_errors


    def deserialization(self) :
        from ..DebugUtility import HtmlClass
        import webbrowser

        call_func = [value for name, value in inspect.getmembers(self, callable)
            if name.startswith('update') and name != "update_BP_mcfunction"]
        for func in call_func : func()

        error_list = [self.RP_load_errors, self.RP_read_errors, self.BP_load_errors, self.BP_read_errors]
        if any(any(len(j) for j in i.values()) for i in error_list) :
            html_content = HtmlClass.WorldLoadHTML
            for ph, data in [
                (r"/*__RP_LOAD_ERRORS__*/{}", self.RP_load_errors),
                (r"/*__RP_READ_ERRORS__*/{}", self.RP_read_errors),
                (r"/*__BP_LOAD_ERRORS__*/{}", self.BP_load_errors),
                (r"/*__BP_READ_ERRORS__*/{}", self.BP_read_errors)]:
                if not any(data.values()) : continue
                new_data = {i:j for i,j in data.items() if j}
                html_content = html_content.replace(ph, json.dumps(new_data), 1)
            uid = self.main_thread.WebsiteRegister(html_content)
            HtmlClass.setTimeOut(2, webbrowser.open_new, f"http://localhost:32323/?tempfile={uid}")

        return self

class DimensionManager:
    """管理多个维度（世界）"""

    def __init__(self, main_thread:"MinecraftSimulator") :
        from .dimension import Dimension, SQLiteDataBase
        self.__dimensions: Dict[str, Dimension] = {}

        for k in Constants.DIMENSION_INFO.keys() :
            self.__dimensions[k] = Dimension(main_thread, k)

    def __tick__(self) :
        for _dim in self.__dimensions.values() :
            _dim.__tick__()


    def get_dimension(self, id:Constants.DimensionID) :
        id = id.replace("minecraft:", "", 1)
        if id not in Constants.DIMENSION_INFO : raise ValueError(f"{id}不是有效的维度名")
        return self.__dimensions.get(id)


    def serialization(self) : 
        for _,dim in self.__dimensions.items() : dim.serialization()

    def deserialization(self) : 
        for _,dim in self.__dimensions.items() : dim.deserialization()

class TickEventScheduler :
    """
    register_interval注册的循环函数
    返回break字符串会终止循环
    """

    def __init__(self) :
        self.__global_tick:int = 0
        self.__events_start:Dict[int, List[Tuple[int, Callable]]] = {}
        self.__events_end:Dict[int, List[Tuple[int, Callable]]] = {}

    def unregister_delay(self, callback, all=False):
        """按对象身份注销 callback。all=True 删全部，否则只删最先找到的一个。"""
        for events in (self.__events_start, self.__events_end):
            for tick, bucket in events.items():
                for time_calls in bucket.copy():
                    interval_time, calls = time_calls
                    if interval_time : continue

                    calls_func = calls.func if isinstance(calls, functools.partial) else calls
                    callback_func = callback.func if isinstance(callback, functools.partial) else callback
                    if calls_func is callback_func : 
                        bucket.remove(time_calls)
                        if not all : return None

    def unregister_interval(self, callback, all=False):
        """按对象身份注销 callback。all=True 删全部，否则只删最先找到的一个。"""
        for events in (self.__events_start, self.__events_end):
            for tick, bucket in events.items():
                for time_calls in bucket.copy():
                    interval_time, calls = time_calls
                    if not interval_time : continue

                    calls_func = calls.func if isinstance(calls, functools.partial) else calls
                    callback_func = callback.func if isinstance(callback, functools.partial) else callback
                    if calls_func.__code__ is callback_func.__code__ : 
                        bucket.remove(time_calls)
                        if not all : return None

    def register_delay(self, tick:int, callback:Callable, end_of_tick=False):
        """注册一个延时事件， tick 后执行一次 callback"""
        if tick <= 0: raise ValueError("tick must be > 0")
        events_save = self.__events_start if not end_of_tick else self.__events_end
        next_run_time = self.__global_tick + tick
        if next_run_time not in events_save : events_save[next_run_time] = []
        events_save[next_run_time].append((0, callback))

    def register_interval(self, tick:int, callback:Callable, end_of_tick=False):
        """注册一个循环事件，每 tick 执行一次 callback"""
        events_save = self.__events_start if not end_of_tick else self.__events_end
        if tick <= 0: raise ValueError("tick must be > 0")
        next_run_time = self.__global_tick + tick
        if next_run_time not in events_save : events_save[next_run_time] = []
        events_save[next_run_time].append((tick, callback))

    def __tick_start__(self) -> None:
        """
        外部循环调用的驱动方法。
        应在主循环中频繁调用（如每帧或每轮事件循环）。
        """
        calls = self.__events_start.get(self.__global_tick, ())
        for interval_time, callback in calls :
            result = callback()
            if result == "break" : continue
            if interval_time : self.register_interval(interval_time, callback)
        if calls : del self.__events_start[self.__global_tick]
        self.__global_tick += 1

    def __tick_end__(self) -> None:
        """
        外部循环调用的驱动方法。
        应在主循环中频繁调用（如每帧或每轮事件循环）。
        """
        calls = self.__events_end.get(self.__global_tick, ())
        for interval_time, callback in calls :
            result = callback()
            if result == "break" : continue
            if interval_time : self.register_interval(interval_time, callback, True)
        if calls : del self.__events_end[self.__global_tick]

class StructureManager:
    """管理 .mcstructure 文件，支持懒加载和双模式保存"""

    def __init__(self, main_thread:"MinecraftSimulator") :
        self.__challenge = main_thread.IsChallenge
        self.__root_dir = main_thread.WorldPath / "structures"
        self.__cache: Dict[str, MCStructureManage.CommonStructure] = {}
        for path in self.__root_dir.glob("*.mcstructure") : 
            self.__cache[path.stem] = path.absolute()

    def __contains__(self, item:str):
        return item in self.__cache

    def __delitem__(self, key:str):
        if key in self.__cache : del self.__cache[key]

    def __set_structure_outside__(self, name:str, path:Path) :
        self.__cache[name] = path

    def get_structure(self, name:str) :
        if name not in self.__cache: return None
        file_path = self.__cache[name]
        if isinstance(self.__cache[name], Path) :
            with open(file_path, 'rb') as _f :
                self.__cache[name] = MCStructureManage.CommonStructure.from_buffer(_f)
        return self.__cache[name]

    def set_structure(self, name:str, structure:CommonStructure, mode:Literal["disk", "memory"]="disk") -> None:
        self.__cache[name] = structure
        if mode == "memory" or self.__challenge : return None
        self.__root_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.__root_dir / f"{name}.mcstructure"
        with open(file_path, 'wb') as _f : structure.save_as(_f)


    def create_structure(self, dimension, start_pos: Sequence[int], end_pos: Sequence[int]) -> CommonStructure:
        from .block import BlockCommandComponent
        from .dimension import Dimension, UnactiveChunksError
        from package.MCBELab.block_entity import GetNbtUID, GenerateCommandBlockNBT
        if not isinstance(dimension, Dimension) : raise ValueError("无效的dimension参数")

        dim_height = dimension.Height
        dim_height_min = dimension.HeightMin
        x1, y1, z1 = (math.floor(i) for i in start_pos[:3])
        x2, y2, z2 = (math.floor(i) for i in end_pos[:3])
        if x1 > x2 : x1, x2 = x2, x1
        if y1 > y2 : y1, y2 = y2, y1
        if z1 > z2 : z1, z2 = z2, z1
        if y1 < dimension.HeightMin : y1 = dimension.HeightMin
        if y2 >= dimension.HeightMax : y2 = dimension.HeightMax-1
        size_x, size_y, size_z = x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1
        StructureObj = CommonStructure((size_x, size_y, size_z))
        target = StructureObj.block_index

        #转移方块调色板数据
        struct_blocks:List[CommonStructure.BLOCKTYPE] = []
        struct_blocks_nbt_int_tag:List[Union[None, int]] = []
        for _permutation in dimension.Permutations :
            struct_block = CommonStructure.BLOCKTYPE(_permutation.name, _permutation.states)
            struct_blocks.append(struct_block)
            __tag = GetNbtUID(_permutation.name)
            if __tag == 1 : struct_blocks_nbt_int_tag.append(1)
            else : struct_blocks_nbt_int_tag.append(None)
        StructureObj.block_palette.__init__(struct_blocks)

        # 涉及的 chunk 范围
        cx_min, cx_max, cz_min, cz_max = x1//16, x2//16, z1//16, z2//16
        # ---- 1. 预校验：所有涉及 chunk 已加载且活跃 ----
        for cx in range(x1//16*16, (x2//16*16)+16, 16):
            for cz in range(z1//16*16, (z2//16*16)+16, 16):
                if not dimension.is_chunk_active((cx, 0, cz)) : 
                    raise UnactiveChunksError(f"区块{(cx, cz)}不是活跃区块")
        # ---- 2. 逐 chunk、逐行切片拷贝 ----
        for cx in range(cx_min, cx_max + 1):
            for cz in range(cz_min, cz_max + 1):
                chunk = dimension.__get_chunk__((cx, cz), False)
                src = chunk.BlockIndex

                # 该 chunk 与请求范围的交集（全局坐标）
                posx_low = max(cx*16, x1)
                posx_high = min(cx*16 + 15, x2)
                chunk_z_low = max(cz*16, z1) % 16
                chunk_z_high = (min(cz*16 + 15, z2) % 16) + 1
                z_len = chunk_z_high - chunk_z_low
                struct_z_low = cz*16 + chunk_z_low - z1        # ★ 外层算一次

                for chunk_x in range(posx_low%16, (posx_high%16)+1) :
                    for chunk_y in range(y1-dim_height_min, y2+1-dim_height_min) :
                        chunk_idx_origin = (chunk_x * dim_height + chunk_y) * 16
                        src_start = chunk_idx_origin + chunk_z_low
                        src_end = chunk_idx_origin + chunk_z_high
                        struct_idx_origin = ((cx*16+chunk_x-x1) * size_y + (chunk_y+dim_height_min-y1)) * size_z
                        tgt_start = struct_idx_origin + struct_z_low
                        tgt_end = tgt_start + z_len
                        scr_sclice = src[src_start:src_end]
                        target[tgt_start:tgt_end] = scr_sclice

                        for idx, block_idx in enumerate(scr_sclice) :
                            if not struct_blocks_nbt_int_tag[block_idx] : continue
                            cb_nbt_tag = GenerateCommandBlockNBT("CommandBlock")
                            if dimension.Permutations[block_idx].states.get("conditional_bit", False) :
                                cb_nbt_tag["conditionalMode"] = nbt.TAG_Byte(1)
                            cb_nbt_tag["TrackOutput"] = nbt.TAG_Byte(0)
                            cb_nbt_tag["Version"] = nbt.TAG_Int(36)

                            BlockObj = chunk.BlockEntities.get(src_start+idx)
                            if not BlockObj : StructureObj.block_nbt[tgt_start+idx] = cb_nbt_tag ; continue
                            _comp:BlockCommandComponent = BlockObj.get_component(BlockCommandComponent)
                            if not _comp : StructureObj.block_nbt[tgt_start+idx] = cb_nbt_tag ; continue
                            cb_nbt_tag["Command"] = nbt.TAG_String(_comp.Command)
                            cb_nbt_tag["CustomName"] = nbt.TAG_String(_comp.CustomName)
                            cb_nbt_tag["auto"] = nbt.TAG_Byte(_comp.Auto)
                            cb_nbt_tag["TickDelay"] = nbt.TAG_Int(_comp.TickDelay)
                            StructureObj.block_nbt[tgt_start+idx] = cb_nbt_tag

        return StructureObj

    def place_structure(self) :
        raise NotImplementedError()

class DebugTerminalManager :

    def __init__(self, main_thread:"MinecraftSimulator") -> None :
        from .. import CommandClass
        from ..DebugUtility import TestDataSave
        self.MainThread = main_thread
        Overworld = self.MainThread.DimensionManager.get_dimension("overworld")

        self.TerminalSending:bool = False
        self.TerminalCommand:str = ""
        self.TerminalRunCallback:Callable[[List[Tuple[int, Union[ParserResult, 
            CommandClass.CompileError, CommandClass.CommandResult]]]], None] = None                #终端命令执行回调函数
        self.DefaultContext = CommandClass.CommandContext("Server", Overworld, [0, 0, 0], [0, 0])

        self.TestFeedbackCache:Dict[int, TestDataSave] = {}

    def __tick__(self) :
        if not self.TerminalSending : return None
        if self.TerminalRunCallback :
            self.TerminalRunCallback(self.__execute())
        self.TerminalCommand = ""
        self.TerminalSending = False

    def __execute(self) :
        from .. import CommandClass
        PASS_PATTERN = re.compile(r'^pass\s+(\d+)$')
        TerminalFeedback:List[Tuple[int, Union[ParserResult, 
            CommandClass.CompileError, CommandClass.CommandResult]]] = []
        RELOAD_PATTERN = re.compile(r'^#reload$')

        lines = self.TerminalCommand.split("\n")
        reload_lines = set()
        # ---------- 预扫描：优先执行 #reload ----------
        for line, raw_line in enumerate(lines):
            content = raw_line.strip()
            if RELOAD_PATTERN.match(content) :
                if not reload_lines :
                    feedback = (line, self.run_command(raw_line))
                    TerminalFeedback.append(feedback)
                reload_lines.add(line)

        skip_remaining = 0
        for line, raw_line in enumerate(lines) :
            content = raw_line.strip()
            if not content : continue             #空行不计入 skip

            # 已经优先执行过的 #reload，跳过
            if line in reload_lines: continue

            # ---------- 1. 分析终端命令，注释无视 skip----------
            if content.startswith("#") :
                feedback = (line, self.run_command(raw_line))
                TerminalFeedback.append( feedback )
                continue

            # ---------- 2. 跳过 ----------
            if skip_remaining > 0 : 
                skip_remaining -= 1
                continue

            # ---------- 3. end：立即终止 ----------
            if content == "end" : break

            # ---------- 4. pass <int> ----------
            re_result = PASS_PATTERN.match(content)
            if re_result :
                skip_remaining = int(re_result.group(1))
                continue

            # ---------- 5. 执行普通命令 ----------
            result = self.MainThread.CommandManager.run_command(
                self.DefaultContext, raw_line, self.MainThread.GameVersion)
            TerminalFeedback.append( (line, result) )

        return TerminalFeedback

    def __create_feedback__(self) :
        from ..DebugUtility import TestDataSave
        tick = self.MainThread.MinecraftWorld.Time.CurrentTick.value
        return self.TestFeedbackCache.setdefault(tick, TestDataSave(self.MainThread))

    def __get_feedback__(self) :
        tick = self.MainThread.MinecraftWorld.Time.CurrentTick.value
        return self.TestFeedbackCache.get(tick)

    def __clear_all_feedback__(self) :
        self.TestFeedbackCache.clear()



    def run_command(self, command:str) :
        from .. import DebugUtility

        call_obj = DebugUtility.Terminal_Compiler(self.MainThread, command)
        if call_obj is None : return None
        elif isinstance(call_obj, ParserResult) : return call_obj
        else : return call_obj(self.DefaultContext, self.MainThread)

    def set_run_callback(self, callback:Callable[[List[Tuple[str, Any]]], None]) :
        self.TerminalRunCallback = callback
    
    def set_command(self, s:str) :
        self.TerminalCommand = s
        self.TerminalSending = True

class SimulatorModule :

    def __init__(self, context:"MinecraftSimulator") :
        from .sundries_type import bind_context
        from .entity import Entity, Player
        from .block  import BlockPermutation
        from .item   import ItemStack
        self.Entity:Type[Entity] = bind_context(context)(Entity)
        self.Player:Type[Player] = bind_context(context)(Player)
        self.ItemStack:Type[ItemStack] = bind_context(context)(ItemStack)
        self.BlockPermutation:Type[BlockPermutation] = bind_context(context)(BlockPermutation)

class CommandManager:

    def __init__(self, simulator:"MinecraftSimulator") :
        from .. import CommandClass
        self.Simulator = simulator
        self.SyntaxErrorData: Dict[str, MCCommandParser.ParserResult] = {}
        self.CompileErrorData: Dict[str, CommandClass.CompileError] = {}
        self.CompileData: Dict[str, RunTimeCallback] = {}

    def compile(self, command:str, version:Tuple[int, int, int]) :
        from .. import CommandClass

        search_key = (command, version)
        if search_key in self.CompileData : return self.CompileData[search_key]
        if search_key in self.CompileErrorData : return self.CompileErrorData[search_key]
        if search_key in self.SyntaxErrorData : return self.SyntaxErrorData[search_key]

        parser_result = MCCommandParser.Start_Tokenizer_V2(command, version)
        if not parser_result.success : 
            self.SyntaxErrorData[search_key] = parser_result
            return parser_result

        call_func = CommandClass.Start_Compile(self.Simulator, parser_result)
        if isinstance(call_func, CommandClass.CompileError): self.CompileErrorData[search_key] = call_func
        else: self.CompileData[search_key] = call_func
        return call_func

    def run_command(self, context, command:str, version:Tuple[int, int, int]) :
        from .. import CommandClass
        context: CommandClass.CommandContext

        if not command.strip() : return None
        search_key = (command, version)
        callback:RunTimeCallback = self.CompileData.get(search_key)

        if not callback : 
            if search_key in self.SyntaxErrorData : return self.SyntaxErrorData.get(search_key)
            if search_key in self.CompileErrorData : return self.CompileErrorData.get(search_key)
            callback = self.compile(command, version)
            if search_key in self.SyntaxErrorData : return self.SyntaxErrorData.get(search_key)
            if search_key in self.CompileErrorData : return self.CompileErrorData.get(search_key)
        if not callable(callback) : raise RuntimeError("Command run faild", callback, command)

        try : response:CommandClass.CommandResult = callback(context, self.Simulator)
        except Exception as e : raise RuntimeError("Command run faild", callback, command) from e
        return response


class MinecraftSimulator :
    
    GameVersion = (26, 50, 0)

    def __init__(self, world_path:Path, challenge:bool=False) :
        from .world import World
        from .entity import Player
        from .loot import LootTableManager

        self.WorldPath = world_path
        self.LevelName = "New_World"                              #模拟名(可赋值)
        self.IsChallenge:bool = challenge                         #每周挑战标志位(不可赋值)
        self.IsGameStartup:bool = False                           #模拟初始化标志位(不可赋值)
        self.IsGameRunning:bool = False                           #模拟开始运行标志位(不可赋值)
        self.IsGameError:bool = False                             #模拟错误终止标志位(不可赋值)
        self.IsGameEnding:bool = False                            #模拟正常停止标志位(不可赋值)

        self.ErrorCallback:Callable[[str, str], None] = None                 #内部代码异常回调函数
        self.WebsiteRegister:Callable[[Union[bytes, str]], str] = None       #临时网页注册函数

        self.SimulatorModule = SimulatorModule(self)                                           # 包含模拟世界上下文的对象
        self.TickScheduler = TickEventScheduler()                                              # 延时/循环事件管理器
        self.StructureManage = StructureManager(self)                                          # mcstructure文件管理器(磁盘交互)
        self.GameSource = StartupGameSource(self)                                              # 定义文件加载器(磁盘交互)
        self.LootManager = LootTableManager(self)                                              # 战利品管理器
        self.MinecraftWorld = World(self)                                                      # 世界数据对象(磁盘交互)
        self.DimensionManager = DimensionManager(self)                                         # 维度管理器(磁盘交互)
        self.CommandManager = CommandManager(self)                                             # 命令管理器
        self.DebugTerminal = DebugTerminalManager(self)                                        # 控制终端管理器

        self.OnlinePlayer:List[Player] = [                                           ]         # 在线玩家列表
        self.LoopThread:threading.Thread = threading.Thread(target=self.__game_looping__)      # Tick循环线程
        self.__GameStopCallback = self.DimensionManager.serialization                          # 游戏停止回调

        try : 
            with open(self.WorldPath/"levelname.txt", mode="r", encoding="utf-8") as _f :
                self.LevelName = _f.read().replace("\n", "")
        except : self.LevelName = "New_World"

    def __setattr__(self, name, value):
        if hasattr(self, "IsGameEnding") and self.IsGameEnding : raise RuntimeError("Simulator实例已停止运行")
        super().__setattr__(name, value)


    def player_serialization(self):
        if self.IsChallenge: return None

        player_file = self.WorldPath / "playerdata.nbt"
        dict1 = nbt.TAG_Compound()
        for player in self.OnlinePlayer: dict1[str(player.UniqueID)] = player.serialization()
        nbt.write_to_nbt_file(player_file, dict1, "gzip", "little")

    def player_deserialization(self):
        if self.IsChallenge: return None
        PlayerType = self.SimulatorModule.Player

        player_file = self.WorldPath / "playerdata.nbt"
        self.OnlinePlayer.clear()
        def reset_player() :
            for i in range(len(self.OnlinePlayer), 5) : 
                _player = PlayerType()
                _player.Dimension = self.DimensionManager.get_dimension("overworld")
                _player.CustomName = "Player" + str(i)
                _player.Pos[0] += np.float32( random.random() * 32 )
                _player.Pos[1] += np.float32( random.random() * 32 )
                _player.Pos[2] += np.float32( random.random() * 32 )
                self.OnlinePlayer.append(_player)

        try : tag = nbt.read_from_nbt_file(player_file, "gzip", "little").get_tag()
        except : reset_player()
        else :
            if not isinstance(tag, nbt.TAG_Compound) : reset_player()
            else :
                for _, player_tag in tag.items() :
                    player = PlayerType.deserialization(player_tag)
                    if isinstance(player, PlayerType): self.OnlinePlayer.append(player)
                if len(self.OnlinePlayer) < 5 : reset_player()


    def __start_up__(self) :
        if self.IsGameEnding : raise RuntimeError("Simulator实例已停止运行")

        self.IsGameStartup = True
        self.GameSource.deserialization()
        self.MinecraftWorld.deserialization()
        self.DimensionManager.deserialization()
        self.player_deserialization()

        self.IsGameStartup = False
        self.IsGameRunning = True
        self.LoopThread.start()

    def __ending__(self) :
        if self.IsGameEnding : raise RuntimeError("Simulator实例已结束")
        self.IsGameRunning = False
        if self.LoopThread.ident is None : return None

        self.LoopThread.join(5)
        if (not self.IsChallenge) and (not self.WorldPath.exists()) :
            os.makedirs(self.WorldPath, exist_ok=True)

        with open(self.WorldPath/"levelname.txt", mode="w+", encoding="utf-8") as _f : 
            _f.write(self.LevelName)
        self.MinecraftWorld.serialization()
        self.player_serialization()
        
        self.IsGameEnding = True

    def __game_looping__(self) :
        while self.IsGameRunning :
            try : 
                self.MinecraftWorld.__tick__()
                self.DimensionManager.__tick__()
                for _player in self.OnlinePlayer : _player.__tick__()
                self.TickScheduler.__tick_start__()
                self.TickScheduler.__tick_end__()
                self.DebugTerminal.__tick__()
            except : 
                self.IsGameRunning = False
                self.IsGameError = True
                if self.ErrorCallback : self.ErrorCallback(
                "游戏运行出现错误\n请查看日志获取详细信息", traceback.format_exc())
                break
            else : time.sleep(0.1)

        self.__GameStopCallback()




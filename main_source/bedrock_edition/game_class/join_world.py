import os,json,re,random
from .. import FileOperation,np,BaseNbtClass,EntityComponent
from . import RunTime
from typing import List,Dict,Union,Literal,Tuple



def rp_animations(game:RunTime.minecraft_thread) :
    rp_path = os.path.join("save_world", game.world_name, 'resource_packs')
    os.makedirs(rp_path, exist_ok=True)
    rp_list = os.listdir(rp_path)
    error:List[str] = []

    for rp_name in rp_list :
        if not FileOperation.is_file(os.path.join(rp_path, rp_name, 'manifest.json')) : continue
        target_path = os.path.join(rp_path, rp_name, 'animations')
        file_list = [i for i in FileOperation.file_in_path(target_path)]
        
        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : content1 = json.loads(file_content)
            except : error.append("载入失败：%s" % file_path)
            else : 
                if 'animations' not in content1 : continue
                for k in content1['animations'] : game.minecraft_ident.animations[k] = {}
    
    return error

def rp_controllers(game:RunTime.minecraft_thread) :
    rp_path = os.path.join("save_world", game.world_name, 'resource_packs')
    os.makedirs(rp_path, exist_ok=True)
    rp_list = os.listdir(rp_path)
    error:List[str] = []

    for rp_name in rp_list :
        if not FileOperation.is_file(os.path.join(rp_path, rp_name, 'manifest.json')) : continue
        target_path = os.path.join(rp_path, rp_name, 'animation_controllers')
        file_list = [i for i in FileOperation.file_in_path(target_path)]
        
        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : content1 = json.loads(file_content)
            except : error.append("载入失败：%s" % file_path)
            else : 
                if 'animation_controllers' not in content1 : continue
                for k in content1['animation_controllers'] : game.minecraft_ident.animation_controllers[k] = {}
    
    return error

def rp_fogs(game:RunTime.minecraft_thread) :
    rp_path = os.path.join("save_world", game.world_name, 'resource_packs')
    os.makedirs(rp_path, exist_ok=True)
    rp_list = os.listdir(rp_path)
    error:List[str] = []

    for rp_name in rp_list :
        if not FileOperation.is_file(os.path.join(rp_path, rp_name, 'manifest.json')) : continue
        target_path = os.path.join(rp_path, rp_name, 'fogs')
        file_list = [i for i in FileOperation.file_in_path(target_path)]
        
        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['minecraft:fog_settings']['description']['identifier']
                if ":" not in k : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.fogs[k] = {}
    
    return error

def rp_particles(game:RunTime.minecraft_thread) :
    rp_path = os.path.join("save_world", game.world_name, 'resource_packs')
    os.makedirs(rp_path, exist_ok=True)
    rp_list = os.listdir(rp_path)
    error:List[str] = []

    for rp_name in rp_list :
        if not FileOperation.is_file(os.path.join(rp_path, rp_name, 'manifest.json')) : continue
        target_path = os.path.join(rp_path, rp_name, 'particles')
        file_list = [i for i in FileOperation.file_in_path(target_path)]
        
        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['particle_effect']['description']['identifier']
                if ":" not in k : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.particles[k] = {}
    
    return error

def rp_sounds(game:RunTime.minecraft_thread) :
    rp_path = os.path.join("save_world", game.world_name, 'resource_packs')
    os.makedirs(rp_path, exist_ok=True)
    rp_list = os.listdir(rp_path)
    error:List[str] = []

    for rp_name in rp_list :
        if not FileOperation.is_file(os.path.join(rp_path, rp_name, 'manifest.json')) : continue
        target_path = os.path.join(rp_path, rp_name, 'sounds', 'sound_definitions')
        
        if FileOperation.is_file(target_path) :
            file_content = FileOperation.read_a_file(target_path)
            try : 
                content1 = json.loads(file_content)
            except : 
                error.append("载入失败：%s" % target_path)
            else : 
                for k in content1 :
                    game.minecraft_ident.sounds[k] = {}
                    if re.search("^record",k) or re.search("^music\\u002egame",k) : continue
                    game.minecraft_ident.musics[k] = {}
    
    return error

def rp_volumes(game:RunTime.minecraft_thread) :
    rp_path = os.path.join("save_world", game.world_name, 'resource_packs')
    os.makedirs(rp_path, exist_ok=True)
    rp_list = os.listdir(rp_path)
    error:List[str] = []

    for rp_name in rp_list :
        if not FileOperation.is_file(os.path.join(rp_path, rp_name, 'manifest.json')) : continue
        target_path = os.path.join(rp_path, rp_name, 'volumes')
        file_list = [i for i in FileOperation.file_in_path(target_path)]
        
        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['minecraft:volume']['description']['identifier']
                if ":" not in k : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.volumeareas[k] = {}
    
    return error



def bp_blocks(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'blocks')
        file_list = [i for i in FileOperation.file_in_path(target_path)]
        
        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['minecraft:block']['description']['identifier']
                if ":" not in k : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.blocks[k] = {}
    
    return error

def bp_items(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'items')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['minecraft:item']['description']['identifier']
                if ":" not in k : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.items[k] = {}
    
    return error

def bp_entities(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'entities')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['minecraft:entity']['description']['identifier']
                if ":" not in k : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : 
                if "is_summonable" not in content1['minecraft:entity']['description'] : content1['minecraft:entity']['description']["is_summonable"] = True
                if "component_groups" not in content1["minecraft:entity"] : content1["minecraft:entity"]["component_groups"] = {}
                if "components" not in content1["minecraft:entity"] : content1["minecraft:entity"]["components"] = {}
                if "events" not in content1["minecraft:entity"] : content1["minecraft:entity"]["events"] = {}
                game.minecraft_ident.entities[k] = content1["minecraft:entity"]
    
    return error

def bp_loot_tables(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'loot_tables')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : content1 = json.loads(file_content)
            except : error.append("载入失败：%s" % file_path)
            else : 
                path1 = file_path.replace(os.path.join(bp_path, bp_name, ""))
                game.minecraft_ident.loot_tables[path1] = content1
    
    return error

def bp_loot_treadings(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'trading')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : content1 = json.loads(file_content)
            except : error.append("载入失败：%s" % file_path)
            else : 
                path1 = file_path.replace(os.path.join(bp_path, bp_name, ""))
                game.minecraft_ident.tradings[path1] = content1
    
    return error

def bp_dialogue(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'dialogue')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                scenes_list = content1['minecraft:npc_dialogue']['scenes']
            except : error.append("载入失败：%s" % file_path)
            else : 
                for scenes in scenes_list :
                    if "scene_tag" in scenes : game.minecraft_ident.dialogues[scenes["scene_tag"]] = {}
    
    return error

def bp_cameras(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'cameras')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = content1['minecraft:camera_preset']['identifier']
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.camera_persets[k] = {}
    
    return error

def bp_recipes(game:RunTime.minecraft_thread) :
    bp_path = os.path.join("save_world", game.world_name, 'behavior_packs')
    os.makedirs(bp_path, exist_ok=True)
    rp_list = os.listdir(bp_path)
    error:List[str] = []

    for bp_name in rp_list :
        if not FileOperation.is_file(os.path.join(bp_path, bp_name, 'manifest.json')) : continue
        target_path = os.path.join(bp_path, bp_name, 'recipes')
        file_list = [i for i in FileOperation.file_in_path(target_path)]

        for file_path in file_list :
            file_content = FileOperation.read_a_file(file_path)
            try : 
                content1 = json.loads(file_content)
                k = None
                for keys in content1 : 
                    try : content1["minecraft:recipe_shaped"]['description']['identifier']
                    except : continue
                    else: k = content1[ 'minecraft:recipe_shapeless']['description']['identifier']
                if k == None : raise Exception
            except : error.append("载入失败：%s" % file_path)
            else : game.minecraft_ident.recipes[k] = {}
    
    return error


def spawn_player(game:RunTime.minecraft_thread) :
    if len(game.minecraft_chunk.player) < 4 :
        for i in range(4-len(game.minecraft_chunk.player)) :
            player1 = BaseNbtClass.entity_nbt().__create__("minecraft:player", 'overworld', 
                [random.randint(-100,100)+0.5, -50, random.randint(-100,100)+0.5],
                "Steve%s" % ("00000%s" % random.randint(1,9999))[-4:])
            player1.SpawnPoint = [np.float32(0.5),np.float32(-50.0),np.float32(0.5)]
            player1.Armor = [{},{},{},{}]
            player1.Weapon = [{},{}]
            player1.ActiveEffects = {}
            player1.EnderChest = [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
            player1.HotBar = [{},{},{},{},{},{},{},{},{}]
            player1.GameMode = np.int8(1)
            player1.PlayerLevel = np.int32(0)
            player1.PlayerLevelPoint = np.float32(0)
            player1.RespawnTime = np.int16(0)
            player1.SelectSlot = np.int16(0)
            player1.Health = np.float32(20)
            player1.fogCommandStack = []
            player1.Ability = {'attackmobs':1,'attackplayer':1,'bulid':1,'flyspeed':0.05,'mayfly':1,'mine':1,
            'op':1,'opencontainers':1,'teleport':1,'worldbuilder':1,'mute':1}
            player1.Attributes['max_health'] = {'Name': 'generic.max_health', 'Base': 20, 'AttributeModifiers': []}
            player1.Inventory = {'Items':[{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}],'container_type':"player","private":False}
            player1.support_nbt += ['SpawnPoint','Armor','Weapon','ActiveEffects',"EnderChest","HotBar","Inventory","GameMode","Ability",
            "PlayerLevel","PlayerLevelPoint","RespawnTime","Health","SelectSlot","fogCommandStack"]

            game.minecraft_chunk.player.append(player1)

def new_version_change(game:RunTime.minecraft_thread) :
    for player1 in game.minecraft_chunk.player :
        player1.Permission = {'camera':'enabled','movement':'enabled'}
        if not hasattr(player1 , "UnlockRecipe") : player1.UnlockRecipe = []
        player1.support_nbt += ['UnlockRecipe']


function_list = [
    rp_animations, rp_controllers, rp_fogs, rp_particles, rp_sounds, rp_volumes,
    bp_blocks, bp_items, bp_entities, bp_loot_tables, bp_loot_treadings, bp_dialogue, bp_cameras, bp_recipes,
    spawn_player, new_version_change
]

def join_game_load(game:RunTime.minecraft_thread) :
    error_list:List[str] = []
    for func in function_list : 
        if not game.in_game_tag : break
        a = func(game)
        if a : error_list.extend(a)
    return error_list




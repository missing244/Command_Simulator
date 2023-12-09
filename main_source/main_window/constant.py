import os,uuid
try : import jnius
except : jnius = None

APP_VERSION = "2.0.0"
PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity') if jnius else None
Context = jnius.autoclass('android.content.Context') if jnius else None

First_Load_Build_Dir = (
    "log", "save_world", "expand_pack", 
    os.path.join("functionality","command"), 
    os.path.join("functionality","structure_output"),
    os.path.join("functionality","example")
)

#ID文件验证列表
ID_File_Path = os.path.join("main_source", "update_source", "import_files")
Prove_ID_List = [
    'animation', 'animation_controller', 'biome', 'block', 'block_loot', 'block_state',
    'damageCause', 'default_chunk', 'default_map', 'effect', 'enchant', 'entity', 'entitySlot',
    'fog', 'gamerule', 'game_data', 'identifier_transfor', 'item', 'loot_table', 'music', 'particle',
    'recipe', 'sound', 'structure', 'trading', 'translate'
]

#世界文件验证列表
world_file_prove = ['level_name','world_info','scoreboard','chunk']

VANILLA_EXPANDS = {
    "android": ["7a41de93-0a65-41e7-8a58-a4223e7161ad", {}],
    "windows": ["4bb65bed-05d0-463c-af81-1140e059dd82", {}],
    "ios": ["3f3443b6-4c0e-4e23-946b-488961152be1", {}]
}
for _platform, _data in VANILLA_EXPANDS.items():
    _data[1]["pack_name"] = "%s 原版拓展" % _platform
    _data[1]["version"] = "" # 留空
del _platform, _data

manifest_json = """
{
    "format_version": 2,
    "header": {
    "uuid": "%s",
    "name": "example_bp",
    "version": [0, 0, 1],
    "description": "This is a example behavior pack",
    "min_engine_version": %s
    },
    "modules": [
      {
        "description": "子资源包简介",
        "version": [0, 0, 1],
        "uuid": "14d5fb6b-ef0a-47e5-8a98-d615709c1a03",
        "type": "data"
      }
    ]
}
"""%(uuid.uuid4(), [1,20,50])

world_config = {
  "normal_setting" : {
    "world_name" : "我的测试", #给你的世界起个名字
    "gamemode" : 1,#玩家模式——0为生存，1为创造，2为冒险，3为观察者
    "difficulty" : 2, #游戏难度——0为和平，1为简单，2为一般，3为困难
    "seed" : 124343354765 , #世界种子——支持字符串和整数两种类型
    "world_data_type" : "infinity", #be世界类型——可填 字符串infinity、flat
    "simulator_distance" : 4 , #模拟距离——允许输入4,6,8,10
  },
  "be_gamerule" : {
    "commandBlockOutput": True, "commandBlocksEnabled": True ,"doDaylightCycle": True ,"doEntityDrops": True,
    "doImmediateRespawn": False, "doInsomnia": True, "doMobLoot": True, "doMobSpawning": True, "doTileDrops": True,
    "doWeatherCycle": True, "drowningDamage": True, "fallDamage": True, "fireDamage": True, "freezeDamage": True, 
    "keepInventory": False, "doFireTick": True, "showTags" : True, "showCoordinates": True, "pvp" : True ,"tntExplodes" : True,
    "functionCommandLimit": 10000, #值需要在0-10000之间
    "maxCommandChainLength": 65536, #值需要在0-2147483647之间
    "randomTickSpeed": 1, #值需要在0-200之间
    "sendCommandFeedback": True, "showDeathMessages": True, "showBorderEffect": True,
    "mobGriefing": True, "naturalRegeneration": True, "respawnblocksexplode": True,
    "spawnRadius" : 5#值需要在0-12之间
  }
}
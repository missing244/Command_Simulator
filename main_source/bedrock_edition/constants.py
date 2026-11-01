import itertools, json, os, zipfile
from typing import Literal
DimensionID = Literal["overworld", "nether", "the_end"]

DIMENSION_INFO = {
    "overworld":{"scale":1, "height":[-64,320], "Time":True},
    "nether":{"scale":8, "height":[0,128], "Time":False},
    "the_end":{"scale":1, "height":[0,256], "Time":False}
}
MITRAX = {
    "rotate": {
        "0_degrees": [[1,0,0],[0,1,0],[0,0,1]],
        "90_degrees": [[0,0,1],[0,1,0],[-1,0,0]],
        "180_degrees": [[-1,0,0],[0,1,0],[0,0,-1]],
        "270_degrees": [[0,0,-1],[0,1,0],[1,0,0]]
    },
    "mirror": {
        "none": [[1,0,0],[0,1,0],[0,0,1]],
        "x": [[1,0,0],[0,1,0],[0,0,-1]],
        "z": [[-1,0,0],[0,1,0],[0,0,1]],
        "xz": [[-1,0,0],[0,1,0],[0,0,-1]]
    }
}

HARDCORE_FILE = zipfile.ZipFile(os.path.realpath(os.path.join(__file__, "..", "hardcore.zip")), "r")
COMMAND_BLOCK_LOAD_CHUNK = set((i, j) for i,j in itertools.product(range(100, 106), range(100, 106)))

__Extend_Data = json.loads(HARDCORE_FILE.read("additional_data.json"))
GAMEMODE = __Extend_Data["gamemode_type"]
DIFFICULT = __Extend_Data["difficult_type"]
HUD_TYPE = __Extend_Data["hud_type"]
INPUT_PERMISSION = __Extend_Data["input_permission"]

BIOME = json.loads(HARDCORE_FILE.read("[SV]biome.json"))
BLOCK_LOOT = json.loads(HARDCORE_FILE.read("[SV]block_loot.json"))
DAMAGE_CAUSE = json.loads(HARDCORE_FILE.read("[SV]damage_cause.json"))
EFFECT = json.loads(HARDCORE_FILE.read("[SV]effect.json"))
ENCHANT = json.loads(HARDCORE_FILE.read("[SV]enchant.json"))
ENTITY_SLOT = json.loads(HARDCORE_FILE.read("[SV]entity_slot.json"))
GAMERULE = json.loads(HARDCORE_FILE.read("[SV]gamerule.json"))
STRUCTURE = json.loads(HARDCORE_FILE.read("[SV]location.json"))

TRANSLATE_ID = json.loads(HARDCORE_FILE.read("translate.json"))

HARDCORE_FILE.close()



















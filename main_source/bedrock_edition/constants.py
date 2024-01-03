import itertools,json,os
from . import FileOperation,np

DIMENSION_INFO = {
    "overworld":{"scale":1, "height":[-64,320]},
    "nether":{"scale":8, "height":[0,128]},
    "the_end":{"scale":1, "height":[0,256]}
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

static_file_path = os.path.join("main_source", "update_source", "import_files")
COMMAND_BLOCK_LOAD_CHUNK = set([(1600+i*16,1600+j*16) for i,j in itertools.product(range(6),repeat=2)])
COMMAND_BLOCK_MAP_INDEX = [i for i in range(7,43) if (not(19 <= i <= 31))]

ENCHANT_TEMPLATE = {"id":"","lvl":np.int16(-1)}
EFFECT_TEMPLATE = {"Id":"","Amplifier":np.int16(-1),"Duration":np.int32(-1)}
WRITTEN_BOOK_TEMPLATE = {'author':"",'title':"",'pages':[]}


try : 
    TRANSLATE_ID = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"translate")))
    GAME_DATA = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"game_data")))
    BLOCK_STATE = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"block_state")))
    BLOCK_LOOT = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"block_loot")))
    IDENTIFIER_TRANSFORM = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"identifier_transfor")))
    DEFAULT_BLOCK_MAP = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"default_map")))
    DEFAULT_CHUNK_DATA = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"default_chunk")))

    BIOME = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"biome")))
    STRUCTURE = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"structure")))
    DAMAGE_CAUSE = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"damageCause")))
    EFFECT = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"effect")))
    ENCHANT = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"enchant")))
    ENTITY_SLOT = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"entitySlot")))
    GAMERULE = json.loads(FileOperation.read_a_file(os.path.join(static_file_path,"gamerule")))
except : pass























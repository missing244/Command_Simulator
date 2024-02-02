from .. import np
import copy

class block_components :
    
    def __init__(self) :
        self.standing_banner = {"Patterns" : [{"Color":"","Pattern":""}]}
        self.wall_banner = {"Patterns" : [{"Color":"","Pattern":""}]}
        self.beacon = {"primary": "","secondary": ""}
        self.bed = {"color":np.int8(0)}
        self.beehive = {"Occupants":[{"ActorIdentifier":"minecraft:bee","TicksLeftToStay":np.int16(0),"SaveData":{}}]}
        self.bee_nest = {"Occupants":[{"ActorIdentifier":"minecraft:bee","TicksLeftToStay":np.int16(0),"SaveData":{}}]}
        self.brewing_stand = {"FuelTotal":np.int16(0),"FuelAmount":np.int16(0),"CookTime":np.int16(0),"Items":[ None for i in range(5) ]}
        self.campfire = {"ItemTime1":np.int16(0),"Item1":None,"ItemTime2":np.int16(0),"Item2":None,
                         "ItemTime3":np.int16(0),"Item3":None,"ItemTime4":np.int16(0),"Item4":None}
        self.soul_campfire = {"ItemTime1":np.int16(0),"Item1":None,"ItemTime2":np.int16(0),"Item2":None,
                              "ItemTime3":np.int16(0),"Item3":None,"ItemTime4":np.int16(0),"Item4":None}
        self.cauldron = {"PotionId":np.int8(-1),"PotionType":np.int8(-1),"CustomColor":np.int32(0)}
        self.chest = {"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(27) ]}
        self.trapped_chest = {"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(27) ]}
        self.barrel = {"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(27) ]}
        self.command_block = {"LastTickActivated":False,"auto":False,"LastExecution":0,"Success":0,"Command":"","CustomName":"[!]","LastOutput":"","TickDelay":np.int32(0)}
        self.chain_command_block = {"LastTickActivated":False,"auto":False,"LastExecution":0,"Success":0,"Command":"","CustomName":"[!]","LastOutput":"","TickDelay":np.int32(0)}
        self.repeating_command_block = {"LastTickActivated":False,"auto":False,"LastExecution":0,"Success":0,"Command":"","CustomName":"[!]","LastOutput":"","TickDelay":np.int32(0)}
        self.dispenser = {"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(9) ]}
        self.droprer = {"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(9) ]}
        self.enchanting_table = {"rott":np.float32(0)}
        self.end_gateway = {"ExitPortal":[np.int32(1827),np.int32(79),np.int32(1872)]}
        self.flower_pot = {"PlantBlock":None}
        self.furnace = {"BurnTime":np.int16(0),"CookTime":np.int16(0),"StoredXPInt":np.int16(0),"Items":[ None for i in range(3) ]}
        self.lit_furnace = {"BurnTime":np.int16(0),"CookTime":np.int16(0),"StoredXPInt":np.int16(0),"Items":[ None for i in range(3) ]}
        self.smoker = {"BurnTime":np.int16(0),"CookTime":np.int16(0),"StoredXPInt":np.int16(0),"Items":[ None for i in range(3) ]}
        self.lit_smoker = {"BurnTime":np.int16(0),"CookTime":np.int16(0),"StoredXPInt":np.int16(0),"Items":[ None for i in range(3) ]}
        self.blast_furnace = {"BurnTime":np.int16(0),"CookTime":np.int16(0),"StoredXPInt":np.int16(0),"Items":[ None for i in range(3) ]}
        self.lit_blast_furnace = {"BurnTime":np.int16(0),"CookTime":np.int16(0),"StoredXPInt":np.int16(0),"Items":[ None for i in range(3) ]}
        self.hopper = {"Items":[ None for i in range(5) ]}
        self.frame = {"ItemRotation":np.float32(0),"ItemDropChance":np.float32(0),"Item":None}
        self.glow_frame = {"ItemRotation":np.float32(0),"ItemDropChance":np.float32(0),"Item":None}
        self.jukebox = {"RecordItem":None}
        self.lectern = {"page":np.int16(0),"book":None}
        self.noteblock = {"note":np.int8(0)}
        self.mob_spawner = {"EntityIdentifier":"","Delay":np.int16(232),"Delay":np.int16(3),"RequiredPlayerRange":np.int16(3)}
        self.shulker_box = {"facing":np.int8(0),"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(27) ]}
        self.undyed_shulker_box = {"facing":np.int8(0),"LootTable":None,"LootTableSeed":np.int32(0),"Items":[ None for i in range(27) ]}

    def find_nbt(self,block_id:str) :
        block_id = block_id.replace("minecraft:","",1)
        if hasattr(self,block_id) : return copy.deepcopy(getattr(self,block_id))

blcok_nbt_data = block_components()

def find_block_id_nbt(block_id:str) : return blcok_nbt_data.find_nbt(block_id)
from typing import List,Dict,Union,Literal,Tuple,Callable
from .. import Constants,np,DataSave,MathFunction,FileOperation
import random,copy,os,json,math,itertools,functools
DIMENSION_LIST = list(Constants.DIMENSION_INFO)


class world_nbt :

    def __init__(self) :

        self.gamemode = np.int8(0)
        self.difficulty =  np.int8(1)
        self.seed = np.int64(0)
        self.world_type = "infinity" #['infinity','flat']
        self.simulator_distance = np.int8(4) #[4,6,8,10]
        self.sunny_time = np.int32(13242)
        self.rain_time = np.int32(0)
        self.thunder_time = np.int32(0)
        self.world_spawn_x = np.float32(0.5)
        self.world_spawn_y = np.float32(-50)
        self.world_spawn_z = np.float32(0.5)
        self.game_time = np.int32(0)
        self.day_time = np.int32(0)
        self.day_count = np.int32(0)

        self.commandblockoutput = True
        self.commandblocksenabled = True
        self.dodaylightcycle = True
        self.doentitydrops = True
        self.dofiretick = True
        self.doimmediaterespawn = False
        self.doinsomnia = True
        self.domobloot = True
        self.domobspawning = True
        self.dotiledrops = True
        self.doweathercycle = True
        self.drowningdamage = True
        self.falldamage = True
        self.firedamage = True
        self.freezedamage = True
        self.keepinventory = True
        self.mobgriefing = True
        self.naturalregeneration = True
        self.pvp = True
        self.respawnblocksexplode = True
        self.sendcommandfeedback = True
        self.showbordereffect = True
        self.showcoordinates = True
        self.showdeathmessages = True
        self.showtags = True
        self.tntexplodes = True
        self.recipesunlock = True
        self.projectilescanbreakblocks = True
        self.showrecipemessages = True
        self.tntexplosiondropdecay = False
        self.dolimitedcrafting = False
        self.showdaysplayed = False

        self.maxcommandchainlength = np.int32(65536)
        self.functioncommandlimit = np.int32(10000)
        self.randomtickspeed = np.int32(1)
        self.spawnradius = np.int32(5)
        self.playerssleepingpercentage = np.int32(100)

        self.mob_event = {
            "events_enabled":True, 
            "minecraft:ender_dragon_event":True, 
            "minecraft:pillager_patrols_event":True,
            "minecraft:wandering_trader_event":True
        }

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "world_nbt"

    def __create__(self, json1:dict) :
        for obj1 in json1['normal_setting'] :
            if obj1 in ["world_name"] : continue
            if not hasattr(self,obj1) : continue
            types1 = self.__getattribute__(obj1)
            self.__setattr__(obj1,types1(json1['normal_setting'][obj1]))

        for obj1 in json1['normal_setting'] :
            obj2 = obj1.lower()
            types1 = self.__getattribute__(obj2)
            self.__setattr__(obj2,types1(json1['be_gamerule'][obj1]))

    def __save__(self) :
        all_data = {}
        for i in self.support_nbt : all_data[i] = self.__getattribute__(i)
        return all_data
    
    def __load__(self, json1:dict) :
        for key1 in [i for i in json1.keys() if (i in self.support_nbt)] :
            data_type = type(self.__getattribute__(key1))
            self.__setattr__(key1,data_type(json1[key1]))
        return self


class item_nbt :

    def __repr__(self) -> str:
        return "<Item %s, %s, %s>" % (self.Identifier, self.Count, self.Damage)

    def __str__(self) -> str :
        return self.tags['Display']['Name']

    def __init__(self) :
        self.Identifier = ""
        self.Count = np.int8(0)
        self.Damage = np.int16(0)
        self.CanDestroy = []
        self.CanPlaceOn = []
        self.LockInInventory = False
        self.LockInSlot = False
        self.KeepOnDeath = False
        self.tags = {'Display':{'Name':"",'Lore':[]}}

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "item_nbt"

    def __create__(self, Identifier:str, Count=1, Damage=0, nbt:dict={}):
        if len(Identifier) == 0 or Identifier == "minecraft:air" : return None
        
        if Identifier in Constants.IDENTIFIER_TRANSFORM['item']['id_transfor'] : 
            self.Identifier = Constants.IDENTIFIER_TRANSFORM['item']['id_transfor'][Identifier]['item_id']
            Damage = Constants.IDENTIFIER_TRANSFORM['block']['id_transfor'][Identifier]['item_data']['value']
        else : self.Identifier = "minecraft:%s" % Identifier if ":" not in Identifier else Identifier

        self.Count = np.int8(Count)
        self.Damage = np.int16(0) if self.Identifier in Constants.GAME_DATA["damage_tool"] else np.int16(Damage)
        if self.Identifier in Constants.GAME_DATA["damage_tool"] : self.tags["damage"] = np.int16(Damage)

        if 'minecraft:keep_on_death' in nbt : self.KeepOnDeath = True

        mmm1 = DataSave.read_json(nbt, ['minecraft:can_destroy','blocks'])
        self.CanDestroy = mmm1 if mmm1 else []

        mmm1 = DataSave.read_json(nbt, ['minecraft:can_place_on','blocks'])
        self.CanDestroy = mmm1 if mmm1 else []

        mmm1 = DataSave.read_json(nbt, ['minecraft:item_lock','mode'])
        if mmm1 and nbt['minecraft:item_lock']['mode'] == 'lock_in_inventory' : self.LockInInventory = True
        elif mmm1 and nbt['minecraft:item_lock']['mode'] == 'lock_in_slot' : self.LockInSlot = True

        item_name = self.Identifier.replace("minecraft:","",1)
        self.tags["Display"]["Name"] = Constants.TRANSLATE_ID["[物品]"].get(item_name, "item.%s.name" % item_name)

        return self

    def __change_to_entity__(self, dimension:Literal["overworld","nether","the_end"], pos:List[Union[float,np.float32]]) :
        nbt1 = {
            "CustomName" : self.tags["Display"]["Name"],
            'Item':{'Identifier':self.Identifier,"Count":self.Count,"Damage":self.Damage,"CanDestroy":self.CanDestroy,
            "CanPlaceOn":self.CanPlaceOn,"LockInInventory":self.LockInInventory,"LockInSlot":self.LockInSlot,
            "KeepOnDeath":self.KeepOnDeath,"tags":self.tags}
        }
        return entity_nbt().__create__("minecraft:item", dimension, pos).__force_write_nbt__(nbt1)

    def __save__(self) :
        all_data = {}
        for i in self.support_nbt : 
            a = getattr(self,i)
            if isinstance(a,(dict,list)) : a = a.copy()
            all_data[i] = a
        return all_data

    def __load__(self, json1) :
        for key1 in json1:
            self.__setattr__(key1,json1[key1])
            self.support_nbt.append(key1)
        return self


class entity_nbt :

    def __repr__(self) -> str :
        return "<Entity %s, %s, %s>" % (self.Identifier, self.CustomName, self.UniqueID)

    def __init__(self) :
        self.Identifier = ""
        self.UniqueID = np.int64(random.randint(-2**33,2**33))
        self.Pos = [np.float32(0.0),np.float32(0.0),np.float32(0.0)]
        self.Rotation = [np.float32(0.0),np.float32(0.0)]
        self.Motion = [np.float32(0.0),np.float32(0.0),np.float32(0.0)]
        self.CustomNameVisible = bool(1)
        self.CustomName = ""
        self.FallDistance = np.float32(0.0)
        self.Fire = np.int16(0)
        self.OnGround = bool(1)
        self.Invulnerable = bool(0)
        self.Dimension = np.int16(0)
        self.PortalCooldown = np.int32(0)
        self.IsAutonomous = bool(0)
        self.Tags = []
        self.FreezingTime = np.int16(0)
        self.Variant = np.int32(0)
        self.MarkVariant = np.int32(0)
        self.Attributes = {}
        self.Collision = {'width':np.float32(0), 'height':np.float32(0)}
        self.FamilyType = []

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "entity_nbt"
        self.damage = {"time_no_hurt":0, "type":None, "value":0, "source":None}
        self.property:Dict[str,Union[str,int,bool,float]] = {}

    def __create__(self, Identifier:str, dimension:Literal["overworld","nether","the_end"], pos:List[np.float32], name:str=None) :
        from . import EntityComponent
        self.Identifier = "minecraft:%s" % Identifier if (":" not in Identifier) else Identifier
        self.Dimension = list(Constants.DIMENSION_INFO).index(dimension) if isinstance(dimension, str) else dimension
        self.Pos = [np.float32(pos[0]), np.float32(pos[1]), np.float32(pos[2])]

        EntityComponent.set_component(self)
        if (self.Identifier == "minecraft:player" or (hasattr(self,"CanModifyName")) and (getattr(self,"CanModifyName"))) and name : 
            self.CustomName = name

        return self
    
    def __force_write_nbt__(self, nbt:dict) :
        for key in nbt : setattr(self, key, nbt[key])
        return self

    def __reload_UID__(self):
        self.UniqueID = np.int64(random.randint(-2**33,2**33))
        return self.UniqueID

    def __update_mainhand__(self):
        if self.Identifier != "minecraft:player" : return None
        self.Weapon[0] = self.HotBar[self.SelectSlot if self.SelectSlot < len(self.HotBar) else self.HotBar]

    def __pickup_item__(self,item_obj:item_nbt) -> bool :
        test_list = ("Identifier","Damage","CanDestroy","CanPlaceOn","LockInInventory","LockInSlot","KeepOnDeath","tags")
        replace_list = ("CanDestroy","CanPlaceOn","LockInInventory","LockInSlot","KeepOnDeath","tags")

        def place_item(list1:List[item_nbt], index:int) :
            if isinstance(list1[index], item_nbt) :
                for attr_test in test_list :
                    if getattr(list1[index], attr_test) != getattr(item_obj, attr_test) : return None

                if list1[index].Identifier in Constants.GAME_DATA['max_count_1_item'] : return None
                elif list1[index].Identifier in Constants.GAME_DATA['max_count_16_item'] : max_count = 16
                else : max_count = 64

                add_count = min(max_count - int(list1[index].Count), int(item_obj.Count))
                list1[index].Count += np.int8(add_count)
                item_obj.Count -= np.int8(add_count)
            else :
                if item_obj.Identifier in Constants.GAME_DATA['max_count_1_item'] : max_count = 1
                elif item_obj.Identifier in Constants.GAME_DATA['max_count_16_item'] : max_count = 16
                else : max_count = 64

                add_count = min(max_count, int(item_obj.Count))
                item_new = item_nbt().__create__(item_obj.Identifier, add_count, item_obj.Damage)
                for attr in replace_list : setattr(item_new, attr, copy.deepcopy(getattr(item_obj, attr)))
                item_obj.Count -= np.int8(add_count)
                list1[index] = item_new

        if self.Identifier == "minecraft:player" :
            for index in range(self.HotBar.__len__()) : 
                if item_obj.Count > 0 : place_item(self.HotBar, index)

        if hasattr(self, "Inventory") :
            for index in range(self.Inventory['Items'].__len__()) : 
                if item_obj.Count > 0 : place_item(self.Inventory['Items'], index)
        
        return item_obj.Count > 0

    def __save__(self) :
        all_data = {}
        for i in self.support_nbt : 
            a = getattr(self,i)
            if isinstance(a,(dict,list)) : a = a.copy()
            all_data[i] = a
        return all_data

    def __load__(self, json1:dict) :
        from . import EntityComponent
        for key1 in json1:
            self.__setattr__(key1,json1[key1])
            self.support_nbt.append(key1)
        EntityComponent.set_default_property(self)
        return self


    def __get_passengers__(self):
        if not hasattr(self,"Passengers") : return None
        passengers_list:List[entity_nbt] = []
        for sit_info in self.Passengers['entity'] :
            if sit_info['entity'] is not None and not isinstance(sit_info['entity'], entity_nbt) : sit_info['entity'] = None
            if hasattr(sit_info['entity'], "Health") and sit_info['entity'].Health <= 0 : sit_info['entity'] = None
            if sit_info['entity'] is None : continue 
            if sit_info['entity'].Identifier == "minecraft:player" : continue
            passengers_list.append(sit_info['entity'])
        return passengers_list

    def __sit_update__(self, player_list:List["entity_nbt"]=[]) :
        if not hasattr(self,"Passengers") : return None
        
        for sit_info in self.Passengers['entity'] :
            if sit_info['entity'] is not None and not isinstance(sit_info['entity'], entity_nbt) : sit_info['entity'] = None
            if player_list and isinstance(sit_info['entity'], entity_nbt) and \
            sit_info['entity'].Identifier == "minecraft:player" and sit_info['entity'] not in player_list :
                aa = [i.UniqueID.value for i in player_list]
                index = aa.index(sit_info['entity'].UniqueID.value)
                sit_info['entity'] = player_list[index]
            if hasattr(sit_info['entity'], "Health") and sit_info['entity'].Health <= 0 : sit_info['entity'] = None
            if sit_info['entity'] is None : continue
            sit_info['entity'].Pos[0] = self.Pos[0] + sit_info['seat_pos'][0]
            sit_info['entity'].Pos[1] = self.Pos[1] + sit_info['seat_pos'][1]
            sit_info['entity'].Pos[2] = self.Pos[2] + sit_info['seat_pos'][2]

    def __sit_remove_player__(self) :
        if not hasattr(self,"Passengers") : return None
        
        for sit_info in self.Passengers['entity'] :
            if sit_info['entity'] is not None and not isinstance(sit_info['entity'], entity_nbt) : sit_info['entity'] = None
            if hasattr(sit_info['entity'], "Health") and sit_info['entity'].Health <= 0 : sit_info['entity'] = None
            if sit_info['entity'] is None : continue 
            if sit_info['entity'].Identifier == "minecraft:player" : sit_info['entity'] = None

    def __sit_start_riding__(self, entity_obj) :
        if not hasattr(self,"Passengers") : return False
        if entity_obj.Identifier == "minecraft:warden" : return False
        
        if self.Passengers['family_types'] :
            test_list = set(entity_obj.FamilyType) & set(self.Passengers['family_types'])
            if not test_list : return False

        for sit_info in self.Passengers['entity'] :
            if sit_info['entity'] is not None and not isinstance(sit_info['entity'], entity_nbt) : sit_info['entity'] = None
            if hasattr(sit_info['entity'], "Health") and sit_info['entity'].Health <= 0 : sit_info['entity'] = None
            if sit_info['entity'] is not None : continue 
            sit_info['entity'] = entity_obj 
            self.__sit_update__()
            return True
    
    def __sit_stop_riding__(self, entity_list:list) :
        """踢出坐骑"""
        if not entity_list : return None
        entity : entity_nbt = None
        index : int = 0

        for index,entity in enumerate(entity_list) :
            sss = entity.__get_passengers__()
            if sss and self in sss : break

        if "sss" not in locals() or not(sss and self in sss) : return None

        for sit_info in entity.Passengers['entity'] :
            if sit_info['entity'] is not None and not isinstance(sit_info['entity'], entity_nbt) : sit_info['entity'] = None
            if hasattr(sit_info['entity'], "Health") and sit_info['entity'].Health <= 0 : sit_info['entity'] = None
            if sit_info['entity'] is None : continue 
            if sit_info['entity'] is self : sit_info['entity'] = None

        return self

    def __sit_evict_riders__(self) :
        """踢出骑手"""
        if not hasattr(self,"Passengers") : return []

        passengers_list:List[entity_nbt] = []
        for sit_info in self.Passengers['entity'] :
            if sit_info['entity'] is not None and not isinstance(sit_info['entity'], entity_nbt) : sit_info['entity'] = None
            if hasattr(sit_info['entity'], "Health") and sit_info['entity'].Health <= 0 : sit_info['entity'] = None
            if sit_info['entity'] is None : continue 
            passengers_list.append(sit_info['entity'])
            sit_info['entity'] = None

        return passengers_list


    def __get_damage__(self, world:world_nbt, damage_type:str, value:Union[int,float], couser:"entity_nbt"=None) -> bool :
        if self.Identifier == "minecraft:player" :
            if self.GameMode == 1 : return False
            if not world.falldamage and damage_type in "fall" : return False
            if not world.firedamage and damage_type in ("fire","lava","fire_tick") : return False
            if not world.freezedamage and damage_type == "freezing" : return False
        if (not hasattr(self, "Health")) or (not hasattr(self, "ActiveEffects")) : return False
        if "fire_resistance" in self.ActiveEffects and damage_type in ["fire","lava","fire_tick"] : return False

        if Constants.DAMAGE_CAUSE[damage_type]['modify_in_tick'] : 
            self.Health -= value ; return True
        else : 
            if self.damage["type"] is None :
                self.Health -= value
                self.damage["type"] = damage_type
                self.damage["time_no_hurt"] = 6
                self.damage["value"] = value
                self.damage["source"] = couser
            return True


class block_nbt :

    def __repr__(self) -> str :
        return "<Block %s, %s>" % (self.Identifier,self.BlockState)

    def __init__(self) :
        self.Identifier:str = ""
        self.BlockState:dict = {}

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "block_nbt"

    def __create__(self, Identifier:str, block_state_info:dict={}) :
        if len(Identifier) == 0 : return None
        Identifier = "minecraft:%s" % Identifier if (":" not in Identifier) else Identifier

        if Identifier in Constants.IDENTIFIER_TRANSFORM['block']['id_transfor'] : 
            block_id_1 = Constants.IDENTIFIER_TRANSFORM['block']['id_transfor'][Identifier]['block_id']
            block_state_info.update( Constants.IDENTIFIER_TRANSFORM['block']['id_transfor'][Identifier]['block_data'] )
            self.Identifier = block_id_1
        else : self.Identifier = Identifier

        if isinstance(block_state_info, int) and self.Identifier in Constants.BLOCK_STATE :
            data_value = bin(block_state_info)
            if data_value in Constants.BLOCK_STATE[self.Identifier] :
                self.BlockState = Constants.BLOCK_STATE[self.Identifier][data_value].copy()
            else : self.BlockState = Constants.BLOCK_STATE[self.Identifier]["default"].copy()
        elif self.Identifier in Constants.BLOCK_STATE :
            self.BlockState = Constants.BLOCK_STATE[self.Identifier]["default"].copy()

            tramsfor_state = Constants.IDENTIFIER_TRANSFORM['block_state']
            for state1 in tramsfor_state :
                if state1 not in block_state_info : continue
                block_state_info[tramsfor_state[state1]["old_name"]] = tramsfor_state[state1]["value_map"][block_state_info[state1]]
                del block_state_info[state1]
            
            self.BlockState.update(block_state_info)

        return self

    def __change_to_entity__(self, dimension:Literal["overworld","nether","the_end"], pos:List[Union[float,np.float32]]) :
        if self.Identifier in Constants.BLOCK_LOOT and "summon" in Constants.BLOCK_LOOT[self.Identifier] :
            return entity_nbt().__create__(Constants.BLOCK_LOOT[self.Identifier]["summon"], dimension, pos)
        else :
            nbt1 = {
                "CustomName" : "", 'Item':{
                'Identifier':"","Count":np.int8(1),"Damage":np.int16(0),"CanDestroy":[],"CanPlaceOn":[],"LockInInventory":False,
                "LockInSlot":False,"KeepOnDeath":False,"tags":{'Display':{'Name':"",'Lore':[]}}
            }}

            if self.Identifier not in Constants.BLOCK_LOOT or Constants.BLOCK_LOOT[self.Identifier]['loot'] == "__self__" :
                nbt1['Item']['Identifier'] = self.Identifier
            elif isinstance(Constants.BLOCK_LOOT[self.Identifier]['loot'], dict) :
                item_of_loot = Constants.BLOCK_LOOT[self.Identifier]['loot']
                nbt1['Item']['Identifier'] = list(item_of_loot)[0]
                nbt1['Item']['Count'] = np.int8( item_of_loot[list(item_of_loot)[0]] )

            item_name = nbt1["Item"]["Identifier"].replace("minecraft:","",1)
            nbt1['Item']['tags']["Display"]["Name"] = Constants.TRANSLATE_ID["[物品]"].get(item_name, "item.%s.name" % item_name).split("/")[0]
            nbt1["CustomName"] = Constants.TRANSLATE_ID["[物品]"].get(item_name, "item.%s.name" % item_name).split("/")[0]

            return entity_nbt().__create__("minecraft:item", dimension, pos).__force_write_nbt__(nbt1)

    def __save__(self) :
        all_data = {}
        for i in self.support_nbt : 
            a = getattr(self,i)
            if isinstance(a,(dict,list)) : a = a.copy()
            all_data[i] = a
        return all_data

    def __load__(self, json1) :
        for key1 in json1:
            self.__setattr__(key1,json1[key1])
            self.support_nbt.append(key1)
        return self


class scoreboard_nbt :

    def __init__(self) :
        self.display_list = None
        self.display_sidebar = None
        self.display_belowname = None
        self.scoreboard_list = {}

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.remove("ID_tracker")
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "scoreboard_nbt"

    def ID_tracker(self, entity:Union[entity_nbt,str]) -> str :
        """将对象转换为计分板假名"""
        if isinstance(entity, entity_nbt) and entity.Identifier == "minecraft:player" : name = entity.CustomName
        elif isinstance(entity, entity_nbt) : name = "%s" % entity.UniqueID
        else : name = entity
        return name


    def ____scb_exists____(self, board_name:str) :
        return board_name in self.scoreboard_list

    def ____score_exists____(self, board_name:str, entity:Union[entity_nbt,str]) :
        if board_name not in self.scoreboard_list : return False
        name = self.ID_tracker(entity)
        return name in self.scoreboard_list[board_name]['entity_list']

    def ____get_score____(self, board_name:str, entity:Union[entity_nbt,str]) -> Union[Exception,np.int32] :
        name = self.ID_tracker(entity)
        if not self.____scb_exists____(board_name) : return Exception
        if not self.____score_exists____(board_name, name) : return Exception
        
        return self.scoreboard_list[board_name]['entity_list'][name]

    def ____get_star_obj____(self)  -> List[str] :
        set1 = set()
        for scb_name in self.scoreboard_list :
            set1.update(self.scoreboard_list[scb_name]['entity_list'])
        return list(set1)


    def __add_scoreboard__(self, board_name:str, predicate:str, display_name:str=None) :
        if self.____scb_exists____(board_name) : return Exception
        
        middle1 = {"display_name": "", "predicate": "", "entity_list": {}}
        if display_name is None : middle1['display_name'] = board_name
        else : middle1['display_name'] = display_name
        middle1['predicate'] = predicate
        self.scoreboard_list[board_name] = middle1

    def __remove_scoreboard__(self, board_name:str) :
        if not self.____scb_exists____(board_name) : return Exception
        
        if self.display_list == board_name : self.display_list = None
        if self.display_belowname == board_name : self.display_belowname = None
        if self.display_sidebar == board_name : self.display_sidebar = None
        del self.scoreboard_list[board_name]

    def __set_display__(self, display_id:str, board_name:str=None) :
        if board_name is not None and not self.____scb_exists____(board_name) : return Exception

        if board_name is None :
            if display_id == "list" : self.display_list = None
            elif display_id == "sidebar" : self.display_sidebar = None
            elif display_id == "belowname" : self.display_belowname = None
            return None
        else :
            if display_id == "list" :
                if self.display_belowname == board_name : self.display_belowname = None
                if self.display_sidebar == board_name : self.display_sidebar = None
                self.display_list = board_name
            elif display_id == "sidebar" :
                if self.display_belowname == board_name : self.display_belowname = None
                if self.display_list == board_name : self.display_list = None
                self.display_sidebar = board_name
            elif display_id == "belowname" :
                if self.display_list == board_name : self.display_list = None
                if self.display_sidebar == board_name : self.display_sidebar = None
                self.display_belowname = board_name


    def __set_random_score__(self, entity_list:List[Union[entity_nbt,str]], board_name:str, score1:int, score2:int) :
        if not self.____scb_exists____(board_name) : return Exception
        for name in [self.ID_tracker(i) for i in entity_list] : 
            self.scoreboard_list[board_name]['entity_list'][name] = np.int32(random.randint(score1,score2))

    def __reset_score__(self, entity_list:List[Union[entity_nbt,str]], board_name:str=None) :
        if board_name and not self.____scb_exists____(board_name) : return Exception

        if board_name :
            for name in [self.ID_tracker(i) for i in entity_list] :
                if not self.____score_exists____(board_name, name) : continue
                del self.scoreboard_list[board_name]['entity_list'][name]
        else :
            for scb,name in itertools.product( list(self.scoreboard_list), [self.ID_tracker(i) for i in entity_list] ) :
                if not self.____score_exists____(scb, name) : continue
                del self.scoreboard_list[scb]['entity_list'][name]

    def __add_score__(self, entity_list:List[Union[entity_nbt,str]], board_name:str, score1:int) :
        if not self.____scb_exists____(board_name) : return Exception
        
        for name in [self.ID_tracker(i) for i in entity_list] :
            if self.____score_exists____(board_name, name) : self.scoreboard_list[board_name]['entity_list'][name] += score1
            else : self.scoreboard_list[board_name]['entity_list'][name] = score1

    def __sub_score__(self, entity_list:List[Union[entity_nbt,str]], board_name:str, score1:int) :
        if board_name and not self.____scb_exists____(board_name) : return Exception
        
        for name in [self.ID_tracker(i) for i in entity_list] :
            if self.____score_exists____(board_name, name) : self.scoreboard_list[board_name]['entity_list'][name] -= score1
            else : self.scoreboard_list[board_name]['entity_list'][name] = -score1

    def __set_score__(self, entity_list:List[Union[entity_nbt,str]], board_name:str, score1:int) :
        if not self.____scb_exists____(board_name) : return Exception
        
        for name in [self.ID_tracker(i) for i in entity_list] :
            self.scoreboard_list[board_name]['entity_list'][name] = np.int32(score1)

    def __test_score__(self, entity_list:List[Union[entity_nbt,str]], board_name:str, score1:int, score2:int) :
        if not self.____scb_exists____(board_name) : return Exception

        if score1 == "*" : score1 = -2147483648
        if score2 == "*" : score2 = 2147483647
        func = lambda name:self.____score_exists____(board_name,name) and score1 <= self.____get_score____(board_name,name) <= score2
        a = filter(func, entity_list)
        return list(a)


    def __equral_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            self.scoreboard_list[board_name1]['entity_list'][name1] = self.____get_score____(board_name2, name2)

    def __exchange_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            m1,m2 = self.____get_score____(board_name1, name1),self.____get_score____(board_name2, name2)
            self.scoreboard_list[board_name1]['entity_list'][name1] = m2
            self.scoreboard_list[board_name2]['entity_list'][name2] = m1

    def __max_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        max_value = max(
            self.scoreboard_list[board_name1]['entity_list'][name1],
            max([self.____get_score____(board_name2,i) for i in filter(func, [self.ID_tracker(i) for i in entity_list2])])
        )
        self.scoreboard_list[board_name1]['entity_list'][name1] = max_value

    def __min_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        min_value = min(
            self.scoreboard_list[board_name1]['entity_list'][name1],
            min([self.____get_score____(board_name2,i) for i in filter(func, [self.ID_tracker(i) for i in entity_list2])])
        )
        self.scoreboard_list[board_name1]['entity_list'][name1] = min_value

    def __add_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            self.scoreboard_list[board_name1]['entity_list'][name1] += self.____get_score____(board_name2, name2)

    def __sub_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            self.scoreboard_list[board_name1]['entity_list'][name1] -= self.____get_score____(board_name2, name2)

    def __mul_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            self.scoreboard_list[board_name1]['entity_list'][name1] *= self.____get_score____(board_name2, name2)

    def __div_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            value1,value2 = self.____get_score____(board_name1, name1), self.____get_score____(board_name2, name2)
            if value2 == 0 : continue
            div_value, mod_value = divmod(value1, value2)
            if mod_value != 0 and value1 < 0 and value2 > 0 : 
                div_value += 1 ; mod_value -= value2
            elif mod_value != 0 and  value1 > 0 and value2 < 0 : 
                div_value -= 1 ; mod_value -= value2
            self.scoreboard_list[board_name1]['entity_list'][name1] = div_value

    def __mod_entity_score__(self, entity1:entity_nbt, board_name1:str, entity_list2:List[Union[entity_nbt,str]], board_name2:str) :
        if not self.____scb_exists____(board_name1) : return Exception
        if not self.____scb_exists____(board_name2) : return Exception

        name1 = self.ID_tracker(entity1)
        if not self.____score_exists____(board_name1, name1) : 
            self.scoreboard_list[board_name1]['entity_list'][name1] = np.int32(0)

        func = lambda n:self.____score_exists____(board_name2, n)
        for name2 in filter(func, [self.ID_tracker(i) for i in entity_list2]) :
            value1,value2 = self.____get_score____(board_name1, name1), self.____get_score____(board_name2, name2)
            if value2 == 0 : continue
            div_value, mod_value = divmod(value1, value2)
            if mod_value != 0 and value1 < 0 and value2 > 0 : 
                div_value += 1 ; mod_value -= value2
            elif mod_value != 0 and value1 > 0 and value2 < 0 : 
                div_value -= 1 ; mod_value -= value2
            self.scoreboard_list[board_name1]['entity_list'][name1] = mod_value


    def __save__(self) :
        all_data = {}
        for i in self.support_nbt : 
            a = getattr(self,i)
            if isinstance(a,(dict,list)) : a = a.copy()
            all_data[i] = a
        return all_data

    def __load__(self, json1:dict) :
        for key1 in json1:
            self.__setattr__(key1,json1[key1])
            self.support_nbt.append(key1)
        return self


class chunk_nbt :

    def __init__(self) :
        self.block_mapping:List[block_nbt] = []
        self.player:List[entity_nbt] = []
        self.disk_structure:Dict[str,structure_nbt] = {}
        self.tickingarea = {}  #name:{"type":"circle|square","radius":1|None,"dimension":"","force_load":[],"preload":False}
        self.volumearea  = {}  #name:{"dimension":"","effect_area":[],"id":""}

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "chunk_nbt"

        self.loading_chunk_pos = {i:set() for i in Constants.DIMENSION_INFO}
        self.loading_chunk = {i:{} for i in Constants.DIMENSION_INFO}
        self.loading_db_file = {i:{} for i in Constants.DIMENSION_INFO}
        self.chunk_example = {"entities":[],"blocks":[],"biomes":[],"structures":[],"nbt_save":{}}

        self.purple_and_orange_command_block:Dict[Tuple[int],None] = {}
        self.command_block_compile_function:Dict[str,functools.partial] = {}
        self.out_load_entity:List[entity_nbt] = []
        #self.schedule_func_load_area = [] {"function":"","will_load":[],"tickingarea":""}
        #self.schedule_func_gametick  = [] {"function":"","gametick_run":int}
        self.memory_structure:Dict[str,structure_nbt] = {}
        self.music_stack = []
        

    def ____in_build_area____(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[float]) -> bool :
        """位置是否处于可建筑区域"""
        hight_min = Constants.DIMENSION_INFO[dimension_id]["height"][0]
        hight_max = Constants.DIMENSION_INFO[dimension_id]["height"][1]
        return hight_min <= block_pos[1] <= hight_max

    def ____in_load_chunk____(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[float]) :
        """位置是否处于加载区块"""
        chunk_pos = (math.floor(block_pos[0])//16*16, math.floor(block_pos[2])//16*16)
        return chunk_pos in self.loading_chunk[dimension_id]

    def ____pos_to_index____(self, block_pos:List[int]) :
        return math.floor(block_pos[1]) * 256 + math.floor(block_pos[2]) * 16 + math.floor(block_pos[0])


    def ____find_block_mapping____(self, block_id:dict, block_info:Union[int,dict], block_obj:block_nbt=None) :
        if block_obj is None : block_obj = block_nbt().__create__(block_id,block_info)

        for index in range(len(self.block_mapping)) :
            test1 = block_obj.Identifier == self.block_mapping[index].Identifier
            test2 = block_obj.BlockState == self.block_mapping[index].BlockState
            if test1 and test2 : return index
        self.block_mapping.append(block_obj)
        return index + 1

    def ____find_block____(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[Union[float,np.float32,int]]) -> int :
        block_int_pos = (math.floor(block_pos[0]), math.floor(block_pos[1]), math.floor(block_pos[2]))
        pos_x, pos_y, pos_z = block_int_pos

        chunk_pos = (pos_x//16*16, pos_z//16*16)
        world_height_min = Constants.DIMENSION_INFO[dimension_id]['height'][0]
        block_pos = (pos_x-chunk_pos[0], pos_y-world_height_min, pos_z-chunk_pos[1])

        return self.loading_chunk[dimension_id][chunk_pos]['blocks'][self.____pos_to_index____(block_pos)]

    def ____find_block_nbt____(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[Union[float,np.float32,int]]) -> Union[dict,None] :
        block_int_pos = (math.floor(block_pos[0]), math.floor(block_pos[1]), math.floor(block_pos[2]))
        pos_x, pos_y, pos_z = block_int_pos

        chunk_pos = (pos_x//16*16, pos_z//16*16)
        world_height_min = Constants.DIMENSION_INFO[dimension_id]['height'][0]
        block_pos = (pos_x-chunk_pos[0], pos_y-world_height_min, pos_z-chunk_pos[1])

        index_str = str(self.____pos_to_index____(block_pos))
        return self.loading_chunk[dimension_id][chunk_pos]['nbt_save'].get(index_str,None)


    def ____set_block____(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[Union[float,np.float32,int]], block_index:int) -> int :
        block_int_pos = (math.floor(block_pos[0]), math.floor(block_pos[1]), math.floor(block_pos[2]))
        pos_x, pos_y, pos_z = block_int_pos

        chunk_pos = (pos_x//16*16, pos_z//16*16)
        world_height_min = Constants.DIMENSION_INFO[dimension_id]['height'][0]
        block_pos = (pos_x-chunk_pos[0], pos_y-world_height_min, pos_z-chunk_pos[1])

        self.loading_chunk[dimension_id][chunk_pos]['blocks'][self.____pos_to_index____(block_pos)] = block_index

    def ____set_block_nbt____(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[Union[float,np.float32,int]], nbt:dict=None) -> Union[dict,None] :
        block_int_pos = (math.floor(block_pos[0]), math.floor(block_pos[1]), math.floor(block_pos[2]))
        pos_x, pos_y, pos_z = block_int_pos

        chunk_pos = (pos_x//16*16, pos_z//16*16)
        world_height_min = Constants.DIMENSION_INFO[dimension_id]['height'][0]
        block_pos = (pos_x-chunk_pos[0], pos_y-world_height_min, pos_z-chunk_pos[1])

        index_str = str(self.____pos_to_index____(block_pos))
        saves = self.loading_chunk[dimension_id][chunk_pos]['nbt_save']
        if nbt is None and index_str in saves : del saves[index_str]
        elif nbt is not None : saves[index_str] = nbt
    

    def __block_pickup_item__(self, dimension_id:Literal["overworld","nether","the_end"], block_pos:List[Union[float,np.float32,int]], item_obj:item_nbt):
        test_list = ("Identifier","Damage","CanDestroy","CanPlaceOn","LockInInventory","LockInSlot","KeepOnDeath","tags")
        replace_list = ("CanDestroy","CanPlaceOn","LockInInventory","LockInSlot","KeepOnDeath","tags")

        def place_item(list1:List[item_nbt], index:int):
            if isinstance(list1[index], item_nbt) :
                for attr_test in test_list :
                    if getattr(list1[index], attr_test) != getattr(item_obj, attr_test) : return None

                if list1[index].Identifier in Constants.GAME_DATA['max_count_1_item'] : return None
                elif list1[index].Identifier in Constants.GAME_DATA['max_count_16_item'] : max_count = 16
                else : max_count = 64

                add_count = min(max_count - int(list1[index].Count), int(item_obj.Count))
                list1[index].Count += np.int8(add_count)
                item_obj.Count -= np.int8(add_count)
            else :
                if item_obj.Identifier in Constants.GAME_DATA['max_count_1_item'] : max_count = 1
                elif item_obj.Identifier in Constants.GAME_DATA['max_count_16_item'] : max_count = 16
                else : max_count = 64

                add_count = min(max_count, int(item_obj.Count))
                item_new = item_nbt().__create__(item_obj.Identifier, add_count, item_obj.Damage)
                for attr in replace_list : setattr(item_new, attr, copy.deepcopy(getattr(item_obj, attr)))
                item_obj.Count -= np.int8(add_count)
                list1[index] = item_new

        nbt = self.____find_block_nbt____(dimension_id, block_pos)
        if 'Items' not in nbt : return None
        for index in range(nbt['Items'].__len__()) : 
            if item_obj.Count > 0 : place_item(nbt['Items'], index)


    def __get_all_load_entity__(self, is_player:bool=False, has_passengers:bool=True) :
        entity_list : List[entity_nbt] = []
        if not is_player :
            for dimension_id in self.loading_chunk :
                for chunk_id in self.loading_chunk[dimension_id] :
                    entity_list.extend(self.loading_chunk[dimension_id][chunk_id]['entities'])
            entity_list.extend(self.out_load_entity)
        entity_list.extend(self.player)
        
        if has_passengers :
            start_index = 0
            while start_index < entity_list.__len__() :
                if hasattr(entity_list[start_index], "Passengers") :
                    for entity in entity_list[start_index].Passengers['entity'] :
                        if not isinstance(entity['entity'], entity_nbt) : continue
                        if hasattr(entity['entity'], "Health") and entity['entity'].Health <= 0 : 
                            entity['entity'] = None
                            continue
                        entity_list.append(entity['entity'])
                start_index += 1

        return entity_list


    def __select_biome__(self, seed:Union[int,str], dimension:Literal["overworld","nether","the_end"], chunk_pos:List[Union[float,np.float32,int]]) :
        list_biome = [i for i in list(Constants.BIOME) if (dimension in Constants.BIOME[i]['dimension'])]
        if len(list_biome) == 0 : return []
        random.seed("%s%s" % (seed,chunk_pos))
        choose_biome : List[str] = []
        for i in range(1 if random.random() > 0.01 else 2) : 
            choose_biome.append(random.choice(list_biome))
        random.seed()
        return choose_biome

    def __select_structure__(self, seed:Union[int,str], dimension:Literal["overworld","nether","the_end"], chunk_pos:List[Union[float,np.float32,int]]):
        list_structure = [i for i in list(Constants.STRUCTURE) if (dimension in Constants.STRUCTURE[i]['dimension'])]
        if len(list_structure) == 0 : return []
        random.seed("%s%s" % (seed,chunk_pos))
        choose_structure : List[str] = []
        if random.random() < 0.1 : choose_structure.append(random.choice(list_structure))
        random.seed()
        return choose_structure

    def ____generate_chunk____(self, world_config:world_nbt, dimension_id:Literal["overworld","nether","the_end"], chunk_pos:List[Union[float,np.float32,int]]):
        chunk_copy = copy.deepcopy(self.chunk_example)
        chunk_pos = (math.floor(chunk_pos[0])//16*16, math.floor(chunk_pos[1])//16*16)
        if dimension_id == "overworld" :
            if world_config.world_type == "infinity" :
                chunk_copy['biomes'] = self.__select_biome__(world_config.seed, dimension_id, chunk_pos)
                chunk_copy['structures'] = self.__select_structure__(world_config.seed, dimension_id, chunk_pos)
                chunk_copy['blocks'] = Constants.DEFAULT_CHUNK_DATA['infinity'].copy()
            elif world_config.world_type == "flat" :
                chunk_copy['biomes'] = ["plains"]
                chunk_copy['structures'] = []
                chunk_copy['blocks'] = Constants.DEFAULT_CHUNK_DATA['flat'].copy()
        else :
            chunk_copy['biomes'] = self.__select_biome__(world_config.seed, dimension_id, chunk_pos)
            chunk_copy['structures'] = self.__select_structure__(world_config.seed, dimension_id, chunk_pos)
            chunk_copy['blocks'] = Constants.DEFAULT_CHUNK_DATA[dimension_id].copy()

        self.loading_chunk[dimension_id][chunk_pos] = chunk_copy


    def ____clear_all_command_block____(self) :
        self.purple_and_orange_command_block.clear()

    def ____register_command_block____(self, cb_pos:Tuple[int], block_index:int) :
        if block_index in Constants.COMMAND_BLOCK_MAP_INDEX and 1600 <= cb_pos[0] <= 1695 and (
            1600 <= cb_pos[2] <= 1695 and cb_pos not in self.purple_and_orange_command_block) :
            a = self.____find_block_nbt____("overworld", cb_pos)
            if a : a["LastTickActivated"] = False
            self.purple_and_orange_command_block[cb_pos] = None
        elif (block_index not in Constants.COMMAND_BLOCK_MAP_INDEX) and (cb_pos in self.purple_and_orange_command_block) :
            del self.purple_and_orange_command_block[cb_pos]

    def ____clear_all_runtime_command____(self) :
        self.command_block_compile_function.clear()

    def ____register_runtime_command____(self, command:str, compile_func:Callable) :
        self.command_block_compile_function[command] = compile_func


    def __add_entity__(self, *entity_list:entity_nbt) :
        for entity1 in entity_list :
            if entity1.Identifier == "minecraft:player" : continue
            chunk_pos = (math.floor(entity1.Pos[0])//16*16, math.floor(entity1.Pos[2])//16*16)
            entity_chunk_list = self.loading_chunk[DIMENSION_LIST[entity1.Dimension]]
            if chunk_pos not in entity_chunk_list and entity1 not in self.out_load_entity :
                self.out_load_entity.append(entity1)
            elif chunk_pos in entity_chunk_list and entity1 not in entity_chunk_list[chunk_pos]["entities"] : 
                entity_chunk_list[chunk_pos]["entities"].append(entity1)

    def __remove_entity__(self, *entity_list:entity_nbt, scoreboard_obj:scoreboard_nbt=None) :
        for entity1 in entity_list :
            if entity1.Identifier == "minecraft:player" : continue
            chunk_pos = (math.floor(entity1.Pos[0])//16*16, math.floor(entity1.Pos[2])//16*16)
            entity_chunk = self.loading_chunk[DIMENSION_LIST[entity1.Dimension]]
            if chunk_pos not in entity_chunk :
                if entity1 not in self.out_load_entity : continue
                self.out_load_entity.remove(entity1)
            else :
                entity_chunk_list = entity_chunk[chunk_pos]["entities"]
                if entity1 in entity_chunk_list : entity_chunk_list.remove(entity1)
            if scoreboard_obj : scoreboard_obj.__reset_score__((entity1,))

    def __summon_entity__(self, difficulty:int, dimension_id:Union[int,Literal["overworld","nether","the_end"]], entity_id:str, 
                          pos:List[Union[float,np.float32]], name:str=None, event:str=None) :
        from .. import EntityComponent
        if not isinstance(dimension_id, str) : dimension_id = DIMENSION_LIST[dimension_id]
        entity_1 = entity_nbt().__create__(entity_id, dimension_id, pos, name)

        if "mob" in entity_1.FamilyType :
            entity_1.Armor = [{},{},{},{}]
            entity_1.Weapon = [{},{}]
            entity_1.ActiveEffects = {}
            entity_1.support_nbt += ['Armor','Weapon','ActiveEffects']

        if difficulty == 0 and ("monster" in entity_1.FamilyType) : return Exception
        chunk_pos = (math.floor(pos[0])//16*16, math.floor(pos[2])//16*16)

        if self.____in_load_chunk____(dimension_id, pos) : self.loading_chunk[dimension_id][chunk_pos]['entities'].append(entity_1)
        else : self.out_load_entity.append(entity_1)
        return entity_1

    def __teleport_entity__(self, victim:List[entity_nbt], destination_dimension:Union[int,Literal["overworld","nether","the_end"]], 
                            destination:Union[List[float],entity_nbt], set_angle:Union[List[float],entity_nbt]=None, check_block=False) :
        DIMENSION = list(Constants.DIMENSION_INFO)
        success_list:List[entity_nbt] = []
        if isinstance(destination,entity_nbt) : destination:List[float] = destination.Pos
        if isinstance(destination_dimension,(int,np.int16)) : destination_dimension = DIMENSION[int(destination_dimension)]

        if check_block :
            if not self.____in_build_area____(destination_dimension, destination) : return Exception
            if not self.____in_load_chunk____(destination_dimension, destination) : return Exception
        
        def check_area_is_air(entity_obj:entity_nbt) :
            pos_start_x = math.floor(destination[0] - entity_obj.Collision['width']/2)
            pos_end_x = math.floor(destination[0] + entity_obj.Collision['width']/2)
            pos_start_y = math.floor(destination[1])
            pos_end_y = math.floor(destination[1] + entity_obj.Collision['height'])
            pos_start_z = math.floor(destination[2] - entity_obj.Collision['width']/2)
            pos_end_z = math.floor(destination[2] + entity_obj.Collision['width']/2)

            a = range(pos_start_x, pos_end_x + 1, 1)
            b = range(pos_start_y, pos_end_y + 1, 1)
            c = range(pos_start_z, pos_end_z + 1, 1)
            for block_pos in itertools.product(a, b, c) :
                if self.____find_block____(destination_dimension, block_pos) > 0 : return True

            return False

        for entity in victim :
            if check_block and check_area_is_air(entity) : continue

            if isinstance(set_angle, (list,tuple)) and len(set_angle) == 2 :
                vec1 = MathFunction.mc_rotation_pos(1,set_angle[0],set_angle[1])
                angle1 = MathFunction.rotation_angle([0,0,0],vec1)
                entity.Rotation[0] = np.float32(angle1[0])
                entity.Rotation[1] = np.float32(angle1[1])
            elif isinstance(set_angle, (list,tuple)) and len(set_angle) == 3 :
                rotated = MathFunction.rotation_angle(destination,set_angle)
                entity.Rotation[0] = np.float32(rotated[0])
                entity.Rotation[1] = np.float32(rotated[1])
            elif isinstance(set_angle, entity_nbt) :
                rotated = MathFunction.rotation_angle(destination,set_angle.Pos)
                entity.Rotation[0] = np.float32(rotated[0])
                entity.Rotation[1] = np.float32(rotated[1])

            entity.Pos[0] = np.float32(destination[0])
            entity.Pos[1] = np.float32(destination[1])
            entity.Pos[2] = np.float32(destination[2])

            chunk_pos_1 = (math.floor(entity.Pos[0])//16*16, math.floor(entity.Pos[2])//16*16)
            chunk_pos_2 = (math.floor(destination[0])//16*16, math.floor(destination[2])//16*16)
            chunk_data1 = self.loading_chunk[DIMENSION[entity.Dimension]].get(chunk_pos_1,None)
            chunk_data2 = self.loading_chunk[destination_dimension].get(chunk_pos_2,None)

            entity.__sit_stop_riding__(self.__get_all_load_entity__())
            if entity.Dimension != DIMENSION.index(destination_dimension) :
                if chunk_data1 : chunk_data1['entities'].extend(entity.__sit_evict_riders__())
                entity.Dimension = DIMENSION.index(destination_dimension)
            success_list.append(entity)
            if entity.Identifier == "minecraft:player" : continue
            if DIMENSION[entity.Dimension] == destination_dimension : continue

            if chunk_data1 and (entity in chunk_data1[chunk_pos_1]['entities']) : chunk_data1[chunk_pos_1]['entities'].remove(entity)
            elif (chunk_data1 is None) and (entity in self.out_load_entity) : self.out_load_entity.remove(entity)

            if chunk_data2 and (entity not in chunk_data2[chunk_pos_2]['entities']) : chunk_data2[chunk_pos_2]['entities'].append(entity)
            elif (chunk_data2 is None) and (entity in self.out_load_entity) : self.out_load_entity.append(entity)
        
        return success_list


    def ____load_chunk_data____(self, world:world_nbt, world_name:str, chunk_radius:int) :
        chunk_radius = int(chunk_radius) ; dimension_list = list(Constants.DIMENSION_INFO)
        player_load_location = {i:[] for i in dimension_list}
        for i in self.player : player_load_location[dimension_list[i.Dimension]].append(
            (math.floor(i.Pos[0])//16*16, math.floor(i.Pos[2])//16*16))

        for keys in dimension_list : self.loading_chunk_pos[keys].clear()

        for keys in player_load_location :
            for player_chunk_x,player_chunk_z in player_load_location[keys] :
                load_range = (
                    player_chunk_x - (chunk_radius*16) , player_chunk_x + 16 + (chunk_radius*16) ,
                    player_chunk_z - (chunk_radius*16) , player_chunk_z + 16 + (chunk_radius*16) ,
                )
                for chunk_pos in itertools.product(range(load_range[0], load_range[1], 16), range(load_range[2], load_range[3], 16)) :
                    if (abs((chunk_pos[0] - player_chunk_x) // 16) + abs((chunk_pos[1] - player_chunk_z) // 16) > 
                    (chunk_radius + (0 if chunk_pos[0] == player_chunk_x or chunk_pos[1] == player_chunk_z else 1))) : continue
                    self.loading_chunk_pos[keys].add(chunk_pos)

        for keys in self.tickingarea :
            self.loading_chunk_pos[self.tickingarea[keys]['dimension']].update([tuple(i) for i in self.tickingarea[keys]['force_load']])
        self.loading_chunk_pos["overworld"].update(Constants.COMMAND_BLOCK_LOAD_CHUNK)

        for keys in self.loading_chunk_pos :
            for will_load_chunk in self.loading_chunk_pos[keys] :
                db_tuple = (will_load_chunk[0]//400*400, will_load_chunk[1]//400*400)
                data_base_name = "db%s" % str(db_tuple)
                db_file_path = os.path.join("save_world", world_name, "chunk_info", keys, data_base_name)

                if (db_file_path not in self.loading_db_file[keys]) : 
                    if not FileOperation.is_file(db_file_path) : self.loading_db_file[keys][db_file_path] = ["" for i in range(25*25)]
                    else : self.loading_db_file[keys][db_file_path] = FileOperation.read_a_file(db_file_path).split("\n")

                save_chunk_pos = ((will_load_chunk[0] - db_tuple[0])//16, (will_load_chunk[1] - db_tuple[1])//16)
                save_index = save_chunk_pos[1] * 25 + save_chunk_pos[0]
                if not self.____in_load_chunk____(keys, (will_load_chunk[0], 0, will_load_chunk[1])) :
                    if self.loading_db_file[keys][db_file_path][save_index] == "" :
                        self.____generate_chunk____(world, keys, will_load_chunk)
                    else :
                        try : json_text = DataSave.zip_to_string(self.loading_db_file[keys][db_file_path][save_index])
                        except : self.____generate_chunk____(world, keys, will_load_chunk)
                        else : self.loading_chunk[keys][will_load_chunk] = json.loads(json_text, object_hook=DataSave.decoding)

    def ____save_outload_chunk_data____(self, world_name:str) :
        for keys in self.loading_chunk :
            for load_chunk in list(self.loading_chunk[keys]) :
                if load_chunk in Constants.COMMAND_BLOCK_LOAD_CHUNK : continue #不进行储存
                if load_chunk in self.loading_chunk_pos[keys] : continue
                db_tuple = (load_chunk[0]//400*400, load_chunk[1]//400*400)
                data_base_name = "db%s" % str(db_tuple)
                db_file_path = os.path.join("save_world", world_name, "chunk_info", keys, data_base_name)

                save_chunk_pos = ((load_chunk[0] - db_tuple[0])//16, (load_chunk[1] - db_tuple[1])//16)
                save_index = save_chunk_pos[1] * 25 + save_chunk_pos[0]
                json1 = json.dumps(self.loading_chunk[keys][load_chunk], default=DataSave.encoding)
                self.loading_db_file[keys][db_file_path][save_index] = DataSave.string_to_zip(json1)
                
                del self.loading_chunk[keys][load_chunk]

    def ____save_and_write_db_file____(self, world_name:str) :
        for keys in self.loading_chunk :
            for load_chunk in self.loading_chunk[keys] :
                if load_chunk in Constants.COMMAND_BLOCK_LOAD_CHUNK : continue
                db_tuple = (load_chunk[0]//400*400, load_chunk[1]//400*400)
                data_base_name = "db%s" % str(db_tuple)
                db_file_path = os.path.join("save_world", world_name, "chunk_info", keys, data_base_name)

                save_chunk_pos = ((load_chunk[0] - db_tuple[0])//16, (load_chunk[1] - db_tuple[1])//16)
                save_index = save_chunk_pos[1] * 25 + save_chunk_pos[0]
                json1 = json.dumps(self.loading_chunk[keys][load_chunk], default=DataSave.encoding)
                self.loading_db_file[keys][db_file_path][save_index] = DataSave.string_to_zip(json1)

        for keys in self.loading_db_file :
            for file_name in self.loading_db_file[keys] :
                FileOperation.write_a_file(file_name, "\n".join(self.loading_db_file[keys][file_name]))


    def __save__(self) :
        all_data = {}
        for i in self.support_nbt : 
            a = getattr(self,i)
            if isinstance(a,(dict,list)) : a = a.copy()
            all_data[i] = a
        return all_data

    def __load__(self, json1:dict) :
        for key1 in json1:
            self.__setattr__(key1,json1[key1])
            self.support_nbt.append(key1)
        return self


class structure_nbt :

    def __init__(self) :
        self.Area = [1,1,1]
        self.BlockMap:List[block_nbt] = []
        self.Block:List[int] = []
        self.BlockNbt:Dict[str,dict] = {}
        self.Entity:List[entity_nbt] = []
        self.Origin:List[int] = []

        self.support_nbt = [i for i in dir(self) if (i[0:2] != "__")]
        self.support_nbt.append("__minecraft_type__")
        self.__minecraft_type__ = "structure_nbt"

    def __create__(self, chunk:chunk_nbt, dimension_id:Literal["overworld","nether","the_end"], 
                   start_pos:List[float], end_pos:List[float], Entities:bool=True, Blocks:bool=True):
        
        start_pos_setting = [math.floor(min(i)) for i in itertools.zip_longest(start_pos, end_pos, fillvalue=0)]
        end_pos_setting = [math.floor(max(i)) for i in itertools.zip_longest(start_pos, end_pos, fillvalue=0)]
        self.Origin = start_pos_setting
        self.BlockMap = chunk.block_mapping.copy()

        if Entities :
            entity_list = [i for i in chunk.__get_all_load_entity__(has_passengers=False) if i.Identifier != "minecraft:player"]
            func = lambda posx,posy,posz : (
                start_pos_setting[0] <= math.floor(posx) <= end_pos_setting[0] and
                start_pos_setting[1] <= math.floor(posy) <= end_pos_setting[1] and
                start_pos_setting[2] <= math.floor(posz) <= end_pos_setting[2]
            )
            def change_pos(entity:entity_nbt) :
                entity = copy.deepcopy(entity)
                passengers = entity.__get_passengers__() ; index = 0
                while index < len(passengers) :
                    passengers[index].__sit_remove_player__()
                    passengers.extend(passengers[index].__get_passengers__())
                    index += 1
                for i in range(3) : entity.Pos[i] -= np.float32(start_pos_setting[i])
                return entity
            self.Entity = [change_pos(i) for i in entity_list if func(i.Pos[0], i.Pos[1], i.Pos[2])]

        self.Area = [i[1]-i[0]+1 for i in itertools.zip_longest(start_pos, end_pos, fillvalue=0)]

        if Blocks :
            for index,pos in enumerate( itertools.product( range(start_pos_setting[0], end_pos_setting[0]+1), 
            range(start_pos_setting[1], end_pos_setting[1]+1), range(start_pos_setting[2], end_pos_setting[2]+1) ) ) :
                if not chunk.____in_build_area____(dimension_id, pos) : block_index = 0
                elif not chunk.____in_load_chunk____(dimension_id, pos) : block_index = 0
                else : block_index = chunk.____find_block____(dimension_id, pos)
                self.Block.append(block_index if self.BlockMap[block_index].Identifier != "minecraft:structure_void" else -1)
                nbt = chunk.____find_block_nbt____(dimension_id, pos)
                if nbt is not None : self.BlockNbt[str(index)] = copy.deepcopy(nbt)
        else : self.Block = [-1] * (self.Area[0] * self.Area[1] * self.Area[2])

        return self

    def __output__(self, chunk:chunk_nbt, dimension_id:Literal["overworld","nether","the_end"], 
                   start_pos:List[float], Rotation:Literal["0_degrees","90_degrees","180_degrees","270_degrees"]="0_degrees", 
                   Mirror:Literal["none","x","z","xz"]="none", Entities:bool=True, Blocks:bool=True, 
                   Present:float=100, Seed:str=None):

        start_pos_setting = [math.floor(i) for i in start_pos]
        rotate_m,mirror_m = Constants.MITRAX["rotate"][Rotation], Constants.MITRAX["mirror"][Mirror]
        end_m = MathFunction.mitrax_transform(rotate_m, mirror_m)
        end_area = MathFunction.vector_transform(self.Area, end_m)
        place_pos_start = [(i+abs(j)-1 if j < 0 else i) for i,j in itertools.zip_longest(start_pos_setting, end_area)]
        block_index_list = [chunk.____find_block_mapping____(None,None,i) for i in self.BlockMap]

        if Blocks :
            for out_block_index,pos in enumerate( itertools.product(range(self.Area[1]), range(self.Area[2]), range(self.Area[0])) ) :
                if Seed : random.seed("%s%s" % (Seed, pos))
                if random.random() * 100 >= Present : continue
                out_pos = MathFunction.vector_transform(pos, end_m)

                if self.Block[out_block_index] < 0 : continue
                place_block_pos = [ i[0] + i[1] for i in itertools.zip_longest(place_pos_start, out_pos, fillvalue=0) ]
                if not chunk.____in_build_area____(dimension_id, place_block_pos) : continue
                if not chunk.____in_load_chunk____(dimension_id, place_block_pos) : continue
                chunk.____set_block____(dimension_id, place_block_pos, block_index_list[self.Block[out_block_index]])

                if str(out_block_index) in self.BlockNbt :
                    chunk.____set_block_nbt____(dimension_id, place_block_pos, copy.deepcopy(self.BlockNbt[str(out_block_index)]) )

        if Seed : random.seed()

        if Entities :
            def register_entity(en2:entity_nbt) :
                en2.__reload_UID__()
                en2_pos = MathFunction.vector_transform(en2.Pos,end_m)
                en2.Pos[0] = np.float32(place_pos_start[0] + en2_pos[0])
                en2.Pos[1] = np.float32(place_pos_start[1] + en2_pos[1])
                en2.Pos[2] = np.float32(place_pos_start[2] + en2_pos[2])
                en2_rotation_pos = MathFunction.mc_rotation_pos(1,en2.Rotation[0],en2.Rotation[1])
                en2_pos_trans = MathFunction.vector_transform(en2_rotation_pos,end_m)
                en2_rotation = MathFunction.rotation_angle([0,0,0],en2_pos_trans)
                en2.Rotation[0] = np.float32(en2_rotation[0])
                en2.Rotation[1] = np.float32(en2_rotation[1])
                passengers = en2.__get_passengers__() ; index = 0
                while index < len(passengers) :
                    passengers[index].__sit_update__()
                    passengers[index].__reload_UID__()
                    passengers.extend(passengers[index].__get_passengers__())
                    index += 1
                if chunk.____in_load_chunk____(dimension_id, en2.Pos) :
                    chunk_pos = (math.floor(en2.Pos[0])//16*16, math.floor(en2.Pos[2])//16*16)
                    chunk.loading_chunk[dimension_id][chunk_pos]['entities'].append(en2)
                else : chunk.out_load_entity.append(en2)

            entity_base = copy.deepcopy(self.Entity)
            for entity in entity_base : register_entity(entity)

    def __save__(self) :
        all_data = {}
        for i in self.support_nbt :
            a = getattr(self,i)
            if isinstance(a,(dict,list)) : a = a.copy()
            all_data[i] = a
        return all_data

    def __load__(self, json1:dict) :
        for key1 in json1:
            self.__setattr__(key1,json1[key1])
            self.support_nbt.append(key1)
        return self


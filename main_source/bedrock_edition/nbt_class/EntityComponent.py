import copy,random,math
from .. import np,Constants



class entity_buliding :


    def set_source(self, source) :
        self.source = source


    def entity_creating(self, entity_object):
        entity_component_json = self.source.entities[entity_object.Identifier]
        
        if "minecraft:rideable" in entity_component_json['components'] :
            self.add_rideable(entity_object, entity_component_json['components']['minecraft:rideable'])

        for i in entity_component_json['components'] :
            if i == "minecraft:rideable" : continue
            func_name = "add_%s"%i.replace("minecraft:","").replace(".","")
            try : func = getattr(self,func_name)
            except : pass
            else : func(entity_object, entity_component_json['components'][i])
        
        self.trigger_entity_event(entity_object, entity_component_json, 'minecraft:entity_spawned')

    def entity_trigger(self, entity_object, event_name:str):
        entity_component_json = self.source.entities[entity_object.Identifier]
        self.trigger_entity_event(entity_object, entity_component_json, event_name)

    def trigger_entity_event(self, entity_object, entity_component_json:dict, event_name:str) :
        events_json = entity_component_json["events"]
        component_groups_json = entity_component_json["component_groups"]
        if event_name not in events_json : return None

        if 'sequence' in events_json[event_name] :
            for sequence_obj in events_json[event_name]['sequence'] :

                if 'randomize' in sequence_obj : sequence_obj = random.choice(sequence_obj['randomize'])

                if 'remove' in sequence_obj and 'component_groups' in sequence_obj['remove'] :
                    for groups_0 in [ i for i in sequence_obj['remove']['component_groups'] if (i in component_groups_json) ] :
                        for component_0 in component_groups_json[groups_0] :
                            try : getattr(self,"remove_%s" % component_0.replace("minecraft:","").replace(".",""))(entity_object)
                            except : pass

                if 'add' in sequence_obj and 'component_groups' in sequence_obj['add'] :
                    for groups_1 in [ i for i in sequence_obj['add']['component_groups'] if (i in component_groups_json) ] :
                        if "minecraft:rideable" in component_groups_json[groups_1] :
                            self.add_rideable(entity_object, component_groups_json[groups_1]['minecraft:rideable'])
                        for component_1 in component_groups_json[groups_1] :
                            if component_1 == 'minecraft:rideable' : continue
                            try : func = getattr(self,"add_%s" % component_1.replace("minecraft:","").replace(".",""))
                            except : pass
                            else : func(entity_object, component_groups_json[groups_1][component_1])

        elif 'remove' in events_json[event_name] :
            if 'component_groups' not in events_json[event_name]['remove'] : return None
            for groups_2 in [i for i in events_json[event_name]['remove']['component_groups'] if (i in component_groups_json)] :
                for component_2 in component_groups_json[groups_2] :
                    try : getattr(self,"remove_%s" % component_2.replace("minecraft:","").replace(".",""))(entity_object)
                    except : pass

        elif 'add' in events_json[event_name] :
            if 'component_groups' not in events_json[event_name]['add'] : return None
            groups_list = [i for i in events_json[event_name]['add']['component_groups'] if (i in component_groups_json)]
            for groups_3 in groups_list :
                if "minecraft:rideable" in component_groups_json[groups_3] :
                    self.add_rideable(entity_object, component_groups_json[groups_3]['minecraft:rideable'])
                for component_3 in component_groups_json[groups_3] :
                    if component_3 == 'minecraft:rideable' : continue
                    try : func = getattr(self,"add_%s" % component_3.replace("minecraft:","").replace(".",""))
                    except : pass
                    else : func(entity_object, component_groups_json[groups_3][component_3])


    def add_rideable(self, entity_obj, json2):
        example = {'entity':[],'family_types':None,'pull_in_entities':False}
        if 'pull_in_entities' in json2 : example['pull_in_entities'] = json2['pull_in_entities']
        if 'family_types' in json2 : example['family_types'] = json2['family_types']
        if 'seat_count' in json2 :
            for i in range(json2['seat_count']) : 
                example['entity'].append({'entity':None,'seat_pos':[np.float32(0),np.float32(0.6),np.float32(0)]})
        else : example['entity'].append({'entity':None,'seat_pos':[np.float32(0),np.float32(0.6),np.float32(0)]})

        entity_obj.Passengers = example
        if 'Passengers' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Passengers')

    def remove_rideable(self, entity_obj):
        if hasattr(entity_obj,'Passengers') : del entity_obj.Passengers
        while 'Passengers' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Passengers')

    def add_addrider(self, entity_obj, json2) :
        from . import BaseNbtClass
        if 'entity_type' not in json2 : return None
        entity_1 = BaseNbtClass.entity_nbt().__create__(json2['entity_type'], 
            list(Constants.DIMENSION_INFO)[entity_obj.Dimension], list(entity_obj.Pos))
        if 'spawn_event' in json2 : self.entity_trigger(json2[entity_1, 'spawn_event'])

        try : entity_obj.Passengers
        except : pass
        else : entity_obj.Passengers['entity'][0]['entity'] = entity_1

    def remove_addrider(self, entity_obj):
        pass

    def add_ageable(self,entity_obj,json2) :
        if 'duration' in json2 : timer1 = np.int32(json2['duration']*20)
        else : timer1 = np.int32(24000)
        entity_obj.AgeCount = timer1
        if 'AgeCount' not in entity_obj.support_nbt : entity_obj.support_nbt.append('AgeCount')

    def remove_ageable(self, entity_obj):
        if hasattr(entity_obj,'AgeCount') : del entity_obj.AgeCount
        while 'AgeCount' in entity_obj.support_nbt : entity_obj.support_nbt.remove('AgeCount')
        
    def add_angry(self,entity_obj,json2):
        if 'duration' in json2 : timer1 = np.int16(json2['duration']*20)
        else : timer1 = np.int16(500)
        entity_obj.AngryCount = timer1
        if 'AngryCount' not in entity_obj.support_nbt : entity_obj.support_nbt.append('AngryCount')

    def remove_angry(self, entity_obj):
        if hasattr(entity_obj,'AngryCount') : del entity_obj.AngryCount
        while 'AngryCount' in entity_obj.support_nbt : entity_obj.support_nbt.remove('AngryCount')
        
    def add_attack(self,entity_obj,json2):
        example = {'Name':"generic.attack_damage",'Base':np.float32(100.0),"AttributeModifiers":[]}
        if 'damage' in json2 and isinstance(json2['damage'],list) : 
            example['Base'] = np.float32(random.uniform(json2['damage'][0],json2['damage'][1]))
        elif 'damage' in json2 and isinstance(json2['damage'],float) :
            example['Base'] = np.float32(json2['damage'])
        elif 'damage' in json2 and isinstance(json2['damage'],dict) : 
            example['Base'] = np.float32(random.uniform(json2['damage']['range_min'],json2['damage']['range_max']))
        entity_obj.Attributes['attack_damage'] = example

    def remove_attack(self, entity_obj):
        if 'attack_damage' in entity_obj.Attributes['attack_damage'] :
            del entity_obj.Attributes['attack_damage']

    def add_breathable(self,entity_obj,json2):
        if 'total_supply' in json2 : Air = np.int16(json2['total_supply']*20)
        else : Air = np.int16(300)
        entity_obj.Air = Air
        if 'Air' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Air')

    def remove_breathable(self, entity_obj):
        if hasattr(entity_obj,"Air") : del entity_obj.Air
        while 'AngryCount' in entity_obj.support_nbt : entity_obj.support_nbt.remove('AngryCount')

    def add_burns_in_daylight(self,entity_obj,json2):
        entity_obj.BurnsLight = True
        if 'BurnsLight' not in entity_obj.support_nbt : entity_obj.support_nbt.append('BurnsLight')

    def remove_burns_in_daylight(self, entity_obj):
        if hasattr(entity_obj,"BurnsLight") : del entity_obj.BurnsLight
        while 'BurnsLight' in entity_obj.support_nbt : entity_obj.support_nbt.remove('BurnsLight')

    def add_collision_box(self,entity_obj,json2):
        example = {'width':np.float32(1),'height':np.float32(1)}
        if 'width' in json2 : example['width'] = np.float32(json2['width'])
        if 'height' in json2 : example['height'] = np.float32(json2['height'])
        entity_obj.Collision = example
        if 'Collision' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Collision')

    def remove_collision_box(self, entity_obj):
        if hasattr(entity_obj,"Collision") : del entity_obj.Collision
        while 'Collision' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Collision')

    def add_despawn(self,entity_obj,json2):
        time1 = np.int16(random.randint(10000,30000))
        if 'Despawn' in json2 : time1 = np.int16(json2['damage_per_hurt'])
        entity_obj.Despawn = time1
        if 'Despawn' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Despawn')

    def remove_despawn(self, entity_obj):
        if hasattr(entity_obj,"Despawn") : del entity_obj.Despawn
        while 'Despawn' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Despawn')

    def add_drying_out_timer(self,entity_obj,json2):
        time1 = np.int16(0)
        if 'total_time' in json2 : time1 = np.int16(json2['total_time']*20)
        entity_obj.Dry = time1
        if not('Dry' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Dry')

    def remove_drying_out_timer(self, entity_obj):
        if hasattr(entity_obj,"Dry") : del entity_obj.Dry
        while 'Dry' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Dry')

    def add_economy_trade_table(self,entity_obj,json2) :
        from . import TradeTable
        example = {}
        if 'table' in json2 : example = TradeTable.generate(self.source,json2['table'])
        entity_obj.Trade = example
        if not('Trade' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Trade')

    def remove_economy_trade_table(self, entity_obj):
        if hasattr(entity_obj,"Trade") : del entity_obj.Trade
        while 'Trade' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Trade')

    def add_experience_reward(self,entity_obj,json2):
        DeathXp = np.int16(0)
        if 'on_death' in json2 and json2['on_death'] != 0 : DeathXp = np.int16(random.randint(2,4))
        entity_obj.DeathXp = DeathXp
        if not('DeathXp' in entity_obj.support_nbt) : entity_obj.support_nbt.append('DeathXp')

    def remove_experience_reward(self, entity_obj):
        if hasattr(entity_obj,"DeathXp") : del entity_obj.DeathXp
        while 'DeathXp' in entity_obj.support_nbt : entity_obj.support_nbt.remove('DeathXp')
    
    def add_flying_speed(self,entity_obj,json2) :
        example = {'Name':"generic.flying_speed",'Base':np.float32(1.0),"AttributeModifiers":[]}
        if 'value' in json2 : example['Base'] = np.float32(json2['value'])
        entity_obj.Attributes['flying_speed'] = example

    def remove_flying_speed(self, entity_obj):
        if 'flying_speed' in entity_obj.Attributes : 
            del entity_obj.Attributes['flying_speed']

    def add_is_baby(self,entity_obj,json2) :
        entity_obj.Baby = True
        if 'Baby' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Baby')

    def remove_is_baby(self, entity_obj):
        if hasattr(entity_obj,"Baby") : del entity_obj.Baby
        while 'Baby' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Baby')
    
    def add_explode(self,entity_obj,json2):
        example = {'breaks_blocks':True,'causes_fire':False,"fuse_length":np.int16(20),'power':np.int8(3)}
        if 'breaks_blocks' in json2 : example['breaks_blocks'] = bool(json2['breaks_blocks'])
        if 'causes_fire' in json2 : example['causes_fire'] = bool(json2['causes_fire'])
        if 'fuse_length' in json2 : example['fuse_length'] = np.int16(json2['fuse_length']*20)
        if 'power' in json2 : example['power'] = np.int8(json2['power'])
        entity_obj.Explode = example
        if 'Explode' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Explode')

    def remove_explode(self, entity_obj):
        if hasattr(entity_obj,"Explode") : del entity_obj.Explode
        while 'Explode' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Explode')

    def add_inventory(self,entity_obj,json2):
        example = {'Items':[],'container_type':"","private":False}
        if 'container_type' in json2 : example['container_type'] = json2['container_type']
        if 'private' in json2 : example['private'] = bool(json2['private'])
        if 'inventory_size' in json2 : 
            for i in range(json2['inventory_size']) : example['Items'].append({})
        else :
            for i in range(5) : example['Items'].append({})
        entity_obj.Inventory = example
        if not('Inventory' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Inventory')

    def remove_inventory(self, entity_obj):
        if hasattr(entity_obj,"Inventory") : del entity_obj.Inventory
        while 'Inventory' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Inventory')

    def add_is_charged(self,entity_obj,json2):
        entity_obj.Powered = True
        if not('Powered' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Powered')

    def remove_is_charged(self, entity_obj):
        if hasattr(entity_obj,"Powered") : del entity_obj.Powered
        while 'Powered' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Powered')
    
    def add_is_illager_captain(self,entity_obj,json2):
        entity_obj.Captain = True
        if not('Captain' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Captain')

    def remove_is_illager_captain(self, entity_obj):
        if hasattr(entity_obj,"Captain") : del entity_obj.Captain
        while 'Captain' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Captain')
    
    def add_is_saddled(self,entity_obj,json2):
        entity_obj.Saddled = True
        if not('Saddled' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Saddled')

    def remove_is_saddled(self, entity_obj):
        if hasattr(entity_obj,"Saddled") : del entity_obj.Saddled
        while 'Saddled' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Saddled')
    
    def add_is_tamed(self,entity_obj,json2):
        entity_obj.Tamed = True
        if not('Tamed' in entity_obj.support_nbt) : entity_obj.support_nbt.append('Tamed')

    def remove_is_tamed(self, entity_obj):
        if hasattr(entity_obj,"Tamed") : del entity_obj.Tamed
        while 'Tamed' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Tamed')
    
    def add_jumpstatic(self,entity_obj,json2) :
        example = {'Name':"generic.jump_strength",'Base':np.float32(0.42),"AttributeModifiers":[]}
        if 'jump_power' in json2 : example['Base'] = np.float32(json2['jump_power'])
        entity_obj.Attributes['jump_strength'] = example

    def remove_jumpstatic(self, entity_obj):
        if "jump_strength" in entity_obj.Attributes : del entity_obj.Attributes['jump_strength']

    def add_loot(self,entity_obj,json2):
        if 'table' in json2 : entity_obj.DeathLootTable = json2['table']
        if not('DeathLootTable' in entity_obj.support_nbt) : entity_obj.support_nbt.append('DeathLootTable')

    def remove_loot(self, entity_obj):
        if hasattr(entity_obj,"DeathLootTable") : del entity_obj.DeathLootTable
        while 'DeathLootTable' in entity_obj.support_nbt : entity_obj.support_nbt.remove('DeathLootTable')

    def add_nameable(self,entity_obj,json2):
        if 'always_show' in json2 : entity_obj.CustomNameVisible = json2['always_show']

    def remove_nameable(self, entity_obj):
        entity_obj.CustomNameVisible = False
    
    def add_persistent(self,entity_obj,json2):
        entity_obj.AlwaysOn = True
        if not('AlwaysOn' in entity_obj.support_nbt) : entity_obj.support_nbt.append('AlwaysOn')

    def remove_persistent(self, entity_obj):
        if hasattr(entity_obj,"AlwaysOn") : del entity_obj.AlwaysOn
        while 'AlwaysOn' in entity_obj.support_nbt : entity_obj.support_nbt.remove('AlwaysOn')
    
    def add_physics(self,entity_obj,json2):
        example = {'has_collision':True,'has_gravity':True}
        if 'has_collision' in json2 : example['has_collision'] = bool(json2['has_collision'])
        if 'has_gravity' in json2 : example['has_gravity'] = bool(json2['has_gravity'])
        entity_obj.Physics = example
        if 'Physics' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Physics')

    def remove_physics(self, entity_obj):
        if hasattr(entity_obj,"Physics") : del entity_obj.Physics
        while 'Physics' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Physics')

    def add_variant(self,entity_obj,json2):
        entity_obj.Variant = np.int16(0)
        if 'value' in json2 : entity_obj.Variant = np.int16(json2['value'])
        if 'Variant' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Variant')

    def remove_variant(self, entity_obj):
        if hasattr(entity_obj,"Variant") : del entity_obj.Variant
        while 'Variant' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Variant')

    def add_timer(self,entity_obj,json2):
        example = {'time_down_event':'','time':20,'loop':False}
        if 'looping' in json2 : example['looping'] = bool(json2['looping'])
        if 'time_down_event' in json2 : example['time_down_event'] = json2['time_down_event']
        if 'time' in json2 and isinstance(json2['time'],list) : 
            example['time'] = np.int16(random.uniform(json2['time'][0],json2['time'][1])*20)
        elif 'time' in json2 and isinstance(json2['time'],(float,int)) : example['time'] = np.int16(json2['time']*20)
        if 'random_time_choices' in json2 : example = json2['random_time_choices'][0]['value']
        try : entity_obj.Timer
        except : entity_obj.Timer = []
        entity_obj.Timer.append(example)
        if 'Timer' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Timer')

    def remove_timer(self, entity_obj):
        if hasattr(entity_obj,"Timer") : del entity_obj.Timer
        while 'Timer' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Timer')

    def add_mark_variant(self,entity_obj,json2):
        entity_obj.MarkVariant = np.int16(0)
        if 'value' in json2 : entity_obj.MarkVariant = np.int16(json2['value'])
        if 'MarkVariant' not in entity_obj.support_nbt : entity_obj.support_nbt.append('MarkVariant')

    def remove_mark_variant(self, entity_obj):
        if hasattr(entity_obj,"MarkVariant") : del entity_obj.MarkVariant
        while 'MarkVariant' in entity_obj.support_nbt : entity_obj.support_nbt.remove('MarkVariant')
    
    def add_movement(self,entity_obj,json2):
        example = {'Name':"generic.movement_speed",'Base':np.float32(0.42),"AttributeModifiers":[]}
        if 'value' in json2 and isinstance(json2['value'], dict) : 
            example['Base'] = np.float32(random.uniform(json2['value']['range_min'],json2['value']['range_max']))
        elif 'value' in json2 and isinstance(json2['value'], (int,float)) : example['Base'] = np.float32(json2['value'])
        entity_obj.Attributes['movement_speed'] = example

    def remove_movement(self, entity_obj):
        if 'movement_speed' in entity_obj.Attributes : 
            del entity_obj.Attributes['movement_speed']
    
    def add_knockback_resistance(self,entity_obj,json2):
        example = {'Name':"generic.knockback_resistance",'Base':np.float32(0),"AttributeModifiers":[]}
        if isinstance(json2,dict) and 'value' in json2 : example['Base'] = np.float32(json2['value'])
        else : example['Base'] = np.float32(json2)
        entity_obj.Attributes['knockback_resistance'] = example

    def remove_knockback_resistance(self, entity_obj):
        if 'knockback_resistance' in entity_obj.Attributes : 
            del entity_obj.Attributes['knockback_resistance']

    def add_follow_range(self,entity_obj,json2):
        example = {'Name':"generic.follow_range",'Base':np.float32(0.42),"AttributeModifiers":[]}
        if isinstance(json2,dict) and 'value' in json2 : example['Base'] = np.float32(json2['value'])
        else : example['Base'] = np.float32(json2)
        entity_obj.Attributes['follow_range'] = example

    def remove_follow_range(self, entity_obj):
        if 'follow_range' in entity_obj.Attributes : del entity_obj.Attributes['follow_range']

    def add_health(self,entity_obj,json2):
        example = {'Name':"generic.max_health",'Base':np.float32(20),"AttributeModifiers":[]}
        if 'value' in json2 and isinstance(json2['value'], dict) : example['Base'] = np.float32(
            random.uniform(json2['value']['range_min'],json2['value']['range_max']))
        elif 'value' in json2 and isinstance(json2['value'], (int,float)) : example['Base'] = np.float32(json2['value'])
        entity_obj.Attributes['max_health'] = example
        entity_obj.Health = np.float32(example['Base'])
        if 'Health' not in entity_obj.support_nbt : entity_obj.support_nbt.append('Health')

    def remove_health(self, entity_obj):
        if 'max_health' in entity_obj.Attributes : del entity_obj.Attributes['max_health']
        if hasattr(entity_obj,"Health") : del entity_obj.Health
        while 'Health' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Health')

    def add_type_family(self,entity_obj,json2):
        if 'family' in json2 : entity_obj.FamilyType = json2['family']

    def remove_type_family(self, entity_obj):
        entity_obj.FamilyType = []
    
    def add_equippable(self,entity_obj,json2):
        equ_json = []
        for slot in json2["slots"] : equ_json.append({"accepted_items":slot["accepted_items"],'Item':None})

        entity_obj.Equippable = equ_json
        if 'Equippable' not in entity_obj.Equippable : entity_obj.support_nbt.append('Equippable')

    def remove_equippable(self, entity_obj):
        if hasattr(entity_obj,"Equippable") : del entity_obj.Equippable
        while 'Equippable' in entity_obj.support_nbt : entity_obj.support_nbt.remove('Equippable')
    
    def add_is_chested(self, entity_obj, json2):
        entity_obj.isChested = True
        if not('isChested' in entity_obj.support_nbt) : entity_obj.support_nbt.append('isChested')

    def remove_is_chested(self, entity_obj):
        if hasattr(entity_obj,"isChested") : del entity_obj.isChested
        while 'isChested' in entity_obj.support_nbt : entity_obj.support_nbt.remove('isChested')
    
    def add_nameable(self, entity_obj, json2):
        if 'always_show' in json2 : entity_obj.CustomNameVisible = json2['always_show']
        entity_obj.CanModifyName = True
        if 'CanModifyName' not in entity_obj.support_nbt : entity_obj.support_nbt.append('CanModifyName')

    def remove_nameable(self, entity_obj):
        if hasattr(entity_obj,"CanModifyName") : del entity_obj.CanModifyName
        while 'CanModifyName' in entity_obj.support_nbt : entity_obj.support_nbt.remove('CanModifyName')



Entity_Construct = entity_buliding()

def set_source(source) :
    Entity_Construct.set_source(source)

def set_component(entity_object) :
    Entity_Construct.entity_creating(entity_object)

def trigger_event(entity_object, event_name:str) :
    Entity_Construct.entity_trigger(entity_object, event_name)
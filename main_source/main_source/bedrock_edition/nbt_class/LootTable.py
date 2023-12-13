from .. import np,Constants
import copy,random

class loot_table :
    
    def spawn_loot(self, source, loot_table_str:str) :
        if loot_table_str not in source.loot_tables : return []
        from .. import BaseNbtClass
        self.source = source
        loot_json = self.source.loot_tables[loot_table_str]
        loot_item_list = self.loot_func(loot_json)
        result_item_list = []
        
        for item_obj in loot_item_list :
            if 'name' not in item_obj : continue
            if item_obj['name'] == "minecraft:air" : continue
            if item_obj['name'] not in source.items : continue

            item_info = {'id':item_obj['name'], 'count':1, 'damage':0}
            if 'functions' in item_obj :
                for func_json in item_obj['functions'] : 
                    if hasattr(self,func_json['function']) : item_info = getattr(self,func_json['function'])(item_info,func_json)
            result_item_list.append(item_info)

        for index,item in enumerate(result_item_list) :
            if ('count' not in item) or (item['count'] <= 0) : continue
            if item["id"] in Constants.GAME_DATA['max_count_1_item'] : item["count"] = min(item["count"],1)
            elif item["id"] in Constants.GAME_DATA['max_count_16_item'] : item["count"] = min(item["count"],16)
            else : item["count"] = min(item["count"],64)

            create_item = BaseNbtClass.item_nbt().__create__(item['id'],item['count'],item['damage'])

            if 'displayname' in item : create_item.tags['Display']['Name'] = item['displayname']
            if 'lore' in item : create_item.tags['Display']['Lore'] = item['lore']
            if 'ench' in item : create_item.tags['ench'] = item['ench']
            if 'writen' in item : create_item.tags['writen'] = item['writen']
            if 'break' in item : create_item.tags['damage'] = item['break']
            result_item_list[index] = create_item

        return result_item_list

    def loot_func(self, loot_json:dict):
        loot_list1 = []
        if 'pools' not in loot_json : return loot_list1

        for loot_pools in loot_json['pools'] :

            if 'tiers' in loot_pools : 
                choose_loot = loot_pools['entries'][random.randint(0, loot_pools['tiers']['initial_range']-1)]
                if choose_loot['type'] == "item" : loot_list1.append(choose_loot)
                elif choose_loot['type'] == "loot_table" : 
                    if choose_loot['name'] not in self.source.loot_tables : continue
                    loot_list1 += self.loot_func(self.source.loot_tables[choose_loot['name']])

            elif 'rolls' in loot_pools :
                choose_count = random.randint(loot_pools['rolls']["min"],loot_pools['rolls']["max"]) if isinstance(loot_pools['rolls'], dict) else loot_pools['rolls']
                for j in range(choose_count) :
                    choose_loot = random.choice(loot_pools['entries'])
                    if choose_loot['type'] == "item" : loot_list1.append(choose_loot)
                    elif choose_loot['type'] == "loot_table" : 
                        if choose_loot['name'] not in self.source.loot_tables : continue
                        loot_list1 += self.loot_func(self.source.loot_tables[choose_loot['name']])
        
        return loot_list1

    def enchant_random_gear(self,item,func_json) :
        if not('ench' in item) : item['ench'] = {}
        if random.random() < func_json['chance'] and item['id'] in self.source.items :
            if len(self.source.items[item['id']]['can_enchant']) :
                ench_name = random.choice(self.source.items[item['id']]['can_enchant'])
                if ench_name not in self.source.enchants : return item
                item['ench'][ench_name] = Constants.ENCHAT_TEMPLATE.copy()
                item['ench'][ench_name]['id'] = ench_name
                item['ench'][ench_name]['lvl'] = np.int16(random.randint(1,self.source.enchants[ench_name]['max_level']))
        return item
    
    def enchant_randomly(self,item,func_json):
        if not('ench' in item) : item['ench'] = {}
        if 'treasure' in func_json and func_json['treasure'] :
            item['ench']['mending'] = Constants.ENCHAT_TEMPLATE.copy()
            item['ench']['mending']['id'] = np.int16(26)
            item['ench']['mending']['lvl'] = np.int16(random.randint(1,1))
        else :
            if len(self.source.items[item['id']]['can_enchant']) :
                ench_name = random.choice(self.source.items[item['id']]['can_enchant'])
                if ench_name not in self.source.enchants : return item
                item['ench'][ench_name] = Constants.ENCHAT_TEMPLATE.copy()
                item['ench'][ench_name]['id'] = ench_name
                item['ench'][ench_name]['lvl'] = np.int16(random.randint(1,self.source.enchants[ench_name]['max_level']))
        return item

    def enchant_with_levels(self,item,func_json):
        if not('ench' in item) : item['ench'] = {}
        if 'treasure' in func_json and func_json['treasure'] :
            item['ench']['mending'] = Constants.ENCHAT_TEMPLATE.copy()
            item['ench']['mending']['id'] = np.int16(26)
            item['ench']['mending']['lvl'] = np.int16(random.randint(1,1))
        else :
            if len(self.source.items[item['id']]['can_enchant']) :
                ench_name = random.choice(self.source.items[item['id']]['can_enchant'])
                if ench_name not in self.source.enchants : return item
                item['ench'][ench_name] = Constants.ENCHAT_TEMPLATE.copy()
                item['ench'][ench_name]['id'] = ench_name
                item['ench'][ench_name]['lvl'] = np.int16(random.randint(1,self.source.enchants[ench_name]['max_level']))
        return item

    def specific_enchants(self,item,func_json):
        if not('ench' in item) : item['ench'] = {}
        if 'enchants' in func_json and len(func_json['enchants']) :
            if not isinstance(func_json['enchants'][0], dict) : return item
            ench_name = random.choice(func_json['enchants'])
            if ench_name["id"] not in self.source.enchants : return item
            item['ench'][ench_name["id"]] = Constants.ENCHAT_TEMPLATE.copy()
            item['ench'][ench_name["id"]]['id'] = ench_name["id"]
            item['ench'][ench_name["id"]]['lvl'] = np.int16(random.randint(1,self.source.enchants[ench_name["id"]]['max_level']))
        return item
                    
    def random_block_state(self,item,func_json):
        if 'values' in func_json :
            if isinstance(func_json['values'],dict) :
                item['damage'] = random.randint(func_json['values']['min'],func_json['values']['max'])
            elif isinstance(func_json['values'],int) : item['damage'] = np.int16(func_json['values'])
        return item
    
    def random_aux_value(self,item,func_json):
        if 'values' in func_json :
            if isinstance(func_json['values'], dict) :
                item['damage'] = random.randint(func_json['values']['min'],func_json['values']['max'])
            elif isinstance(func_json['values'], int) : item['damage'] = np.int16(func_json['values'])
        return item
        
    def set_banner_details(self,item,func_json):
        if item['id'] == 'minecraft:banner' : item['damage'] = np.int16(func_json['type'])
        return item

    def set_book_contents(self,item,func_json):
        item['writen'] = copy.deepcopy(Constants.WRITTEN_BOOK_TEMPLATE)
        if 'author' in func_json : item['writen']['author'] = func_json['author']
        if 'title' in func_json : item['writen']['title'] = func_json['title']
        if 'pages' in func_json : item['writen']['pages'] = func_json['pages']
        return item

    def set_count(self,item,func_json):
        if 'count' not in func_json : return item
        if isinstance(func_json['count'], int) : item['count'] = func_json['count']
        elif isinstance(func_json['count'], dict) : 
            item['count'] = random.randint(func_json['count']['min'],func_json['count']['max'])
        return item
            
    def set_damage(self,item,func_json):
        if 'damage' not in func_json : return item
        if isinstance(func_json['damage'], (float,int)) and self.source.items[item['id']]['damage_max'] : 
            item['break'] = np.int16(func_json['damage'] * self.source.items[item['id']]['damage_max'])
        elif isinstance(func_json['damage'], dict) : 
            present = random.uniform(func_json['damage']['min'],func_json['damage']['max'])
            item['break'] = np.int16(present * self.source.items[item['id']]['damage_max'])
        return item
    
    def set_data(self,item,func_json):
        if 'data' not in func_json : return item
        if isinstance(func_json['data'], (float,int)) : item['damage'] = func_json['data']
        elif isinstance(func_json['data'], dict) : 
            item['count'] = random.randint(func_json['data']['min'],func_json['data']['max'])
        return item

    def set_lore(self,item,func_json):
        item['lore'] = func_json['lore']
        return item

    def set_name(self,item,func_json):
        item['displayname'] = func_json['name']
        return item




generate_loot = loot_table()
def generate(source, loot_table_str:str) :
    return generate_loot.spawn_loot(source, loot_table_str)

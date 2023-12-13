import random
from .. import np


def to_item(source, json1:dict) :
    from .. import BaseNbtClass
    if "choice" in json1 : json1 = random.choice(json1["choice"])
    if "item" not in json1 : return None

    id_split_list = json1['item'].split(":")
    if id_split_list.__len__() < 2 : return None
    item_id = "%s:%s" % (id_split_list[0], id_split_list[1])
    if item_id not in source.items : return None

    if "quantity" in json1 : count1 = json1["quantity"]
    else : count1 = 1

    if len(id_split_list) > 2 : data_value = np.int8(id_split_list[2])
    else : data_value = 0

    return BaseNbtClass.item_nbt().__create__(item_id,count1,data_value)


def generate(source, trade_table_str:str) :
    if trade_table_str not in source.tradings : return []
    trade_json = source.tradings[trade_table_str]
    
    trade_nbt = []
    commodity1 = {"buyA":None, "buyB":None, "sell":None, "maxUses":np.int16(18)}

    for tiers_obj in trade_json['tiers'] :
        if 'groups' in tiers_obj : tiers_1 = random.choice(random.choice(tiers_obj['groups'])['trades'])
        elif 'trades' in tiers_obj : tiers_1 = random.choice(tiers_obj['trades'])
        else : continue
            
        commodity = commodity1.copy()

        if "choice" in tiers_1["wants"] : buy_item = random.choice(tiers_1["wants"]["choice"])
        else : buy_item = tiers_1["wants"]
        if "choice" in tiers_1["gives"] : sell_item = random.choice(tiers_1["gives"]["choice"])
        else : sell_item = tiers_1["gives"][0]

        commodity["sell"] = to_item(source,sell_item)
        if len(buy_item) > 0 : commodity["buyA"] = to_item(source,buy_item[0])
        if len(buy_item) > 1 : commodity["buyB"] = to_item(source,buy_item[1])

    return trade_nbt
    
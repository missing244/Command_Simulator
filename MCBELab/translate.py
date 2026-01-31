import json, os

CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
Translate = json.load(fp=open(os.path.join(CurrentPath, "res", "translate.json"), "r", encoding="utf-8"))
ItemTranslateData = Translate["Item"]
BlockTranslateData = Translate["Block"]
EntityTranslateData = Translate["Entity"]
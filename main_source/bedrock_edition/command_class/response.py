from typing import Mapping,List
from string import Template
import json
from . import COMMAND_CONTEXT,ID_tracker

class Function_Response_Group :

    def __repr__(self) -> str:
        return "<%s Context:%s>" % (self.MCfunction_Name, self.Context)

    def __init__(self, func_name:str, context:COMMAND_CONTEXT) -> None:
        self.MCfunction_Name = func_name
        self.Context = context
        self.Count = 0
        self.is_End = False
        self.Response_List : List[Response_Template]  = []

    def add_response(self, obj:"Response_Template") :
        if not isinstance(obj, Response_Template) : raise TypeError("Not Response_Template Type")
        self.Response_List.append(obj)

    def push_context(self) :
        return "执行者 %s 在%s位置，维度%s，朝向%s，执行函数 %s%s" % (ID_tracker(self.Context["executer"]),
        self.Context["pos"], self.Context["dimension"], self.Context["rotate"], self.MCfunction_Name,
        "" if self.is_End else "(函数未结束)")
    
    def pop_context(self) :
        return "函数 %s 已退出" % self.MCfunction_Name


class Response_Template(Template) :

    def __repr__(self) -> str:
        return "<Response %s>" % json.dumps(self.command_msg)
    
    def __bool__(self) :
        return bool(self.success_count)

    def __init__(self, template:str, success_count:int=0, result_count:int=0, mcfunction:bool=False, response_id:int=None) :
        super().__init__(template)
        self.response_id = response_id
        self.command = ""
        self.command_msg = ""
        self.success_count = int(bool(success_count))
        self.result_count  = int(result_count)
        self.Function_Feedback:List[Function_Response_Group] = [] if mcfunction else None

    def set_command(self, command:str) :
        self.command = command
        return self

    def add_function_feedback(self, obj:Function_Response_Group) :
        if not isinstance(obj, Function_Response_Group) : raise TypeError("Not Function_Response_Group Type")
        self.Function_Feedback.append(obj)
        return self

    def substitute(self, __mapping: Mapping[str, object] = ..., **kwds: object) :
        self.command_msg = super().substitute(__mapping, **kwds)
        return self




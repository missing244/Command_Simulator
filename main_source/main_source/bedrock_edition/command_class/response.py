from typing import Mapping,List
from string import Template
from . import COMMAND_CONTEXT,ID_tracker

class Function_Response_Group :

    def __init__(self, func_name:str, context:COMMAND_CONTEXT) -> None:
        self.MCfunction_Name = func_name
        self.Context = context
        self.Response_List : List[Response_Template]  = []

    def add_response(self, obj) :
        if not isinstance(obj, Response_Template) : raise TypeError("Not Response_Template Type")
        self.Response_List.append(obj)

    def push_context(self) :
        return "执行者 %s 在%s位置，维度%s，朝向%s，执行函数 %s" % (ID_tracker(self.Context["executor"]),
        self.Context["pos"], self.Context["dimension"], self.Context["rotate"], self.MCfunction_Name)
    
    def pop_context(self) :
        return "函数 %s 已退出" % self.MCfunction_Name


class Response_Template(Template) :

    def __init__(self, template:str, success_count:int=0, result_count:int=0, mcfunction:bool=False) :
        super().__init__(template)
        self.command = ""
        self.command_msg = ""
        self.success_count = success_count
        self.result_count  = result_count
        self.Function_Feedback:List[Function_Response_Group] = [] if mcfunction else None

    def set_command(self, command:str) :
        self.command = command
        return self

    def add_function_feedback(self, obj:Function_Response_Group) :
        self.Function_Feedback.append(obj)
        return self

    def substitute(self, __mapping: Mapping[str, object] = ..., **kwds: object) :
        self.command_msg = super().substitute(__mapping, **kwds)
        return self




import os,webbrowser,threading,time,json,itertools
from typing import List,Dict,Union,Literal,Tuple,Generator
from string import Template
from .. import Response
import types


def setTimeOut(sleep_time,func,*args1) :
    def time_out_func(sleep_time,func,*args1) :
        time.sleep(sleep_time)
        func(*args1)
    threading.Thread(target=time_out_func,args=(sleep_time,func,*args1)).start()


class generate_command_block_html :
    
    def __init__(self,cb_list1:dict) -> None:
        self.cb_id_in_js = ["command_block","command_block_condition","chain_command_block","chain_command_block_condition",
                            "repeating_command_block","repeating_command_block_condition"]
        self.cb_list = cb_list1
        
        html_file = open(os.path.join("main_source","bedrock_edition","command_class","trans_html","command_block.html"),"r",encoding="utf-8")
        self.example_html = html_file.read()
        html_file.close()
    
    def encode_for_js(self) :
        self.cb_list_for_js = []
        for index1 in list(self.cb_list) : 
            new_pos = [index1[0]-1600+0.5,index1[1]+64+0.5,index1[2]-1600+0.5]
            block_id = self.cb_list[index1]['id'].replace("minecraft:","",1)
            facing_direction = self.cb_list[index1]['block_state']['facing_direction']
            conditional = self.cb_list[index1]['block_state']['conditional_bit']
            self.cb_list_for_js.append({"id":block_id, "pos":new_pos, "facing":facing_direction, "conditional":conditional})
        return self

    def generate_html(self,file_name:str) :
        file1 = open(os.path.join("html_output",file_name),"w+",encoding="utf-8")
        file1.write(Template(self.example_html).substitute(cb_list = json.dumps(self.cb_list_for_js, separators=(',', ':'))))
        file1.close()
        setTimeOut(1.5, lambda: webbrowser.open("http://localhost:32323/%s" % file_name))


class generate_all_command_load_html :

    def __init__(self) -> None:
        self.req_list = (
            Template('<p class="success_color">该项目没有任何问题</p>'),
            Template('<p class="error_color">以下文件无法使用 utf-8 载入，请注意文件保存编码<br>$file_name</p>'),
            Template("""
				<div class="error_color respone_temp">
					<div style="border-bottom: 3px solid black;"><span>$file_path<br>版本：$version</span><div style="height: 3px;"></div></div>
					<div style="border-bottom: 3px solid black;">第$lines行<br>$command<div style="height: 3px;"></div></div>
					<div>$respone<div style="height: 3px;"></div></div>
				</div>"""
            )
        )

        self.command_block_file_encode:List[str] = None
        self.command_block_file_syntax:Dict[str,List[Tuple]] = None
        self.function_file_encode:List[str] = None
        self.function_file_syntax:Dict[str,List[Tuple]] = None
        
        self.result_command_block_file_info:str = None
        self.result_function_file_info:str = None
        self.result_function_file_req:str = None
        self.result_command_block_file_req:str = None

        html_file = open(os.path.join("main_source","bedrock_edition","command_class","trans_html","command_load.html"),"r",encoding="utf-8")
        self.example_html = html_file.read()
        html_file.close()

    def html_word_replace(self, text1:str) :
        text1 = text1.replace(" ","&nbsp;")
        text1 = text1.replace("<","&#60;")
        text1 = text1.replace(">","&#62;")
        text1 = text1.replace("\n","<br>")
        return text1

    def write_cb_file_encode(self, list1) :
        self.command_block_file_encode = list1
        return self

    def write_cb_file_syntax(self, list1) :
        self.command_block_file_syntax = list1
        return self

    def write_func_file_encode(self, list1) :
        self.function_file_encode = list1
        return self

    def write_func_file_syntax(self, list1) :
        self.function_file_syntax = list1
        return self

    def encode_for_html(self) :
        if not self.command_block_file_encode : self.result_command_block_file_info = self.req_list[0].substitute()
        else :
            file_name = [self.html_word_replace(i) for i in self.command_block_file_encode]
            self.result_command_block_file_info = self.req_list[1].substitute(file_name = "<br>".join(file_name))

        if not self.function_file_encode : self.result_function_file_info = self.req_list[0].substitute()
        else :
            file_name = [self.html_word_replace(i) for i in self.function_file_encode]
            self.result_command_block_file_info = self.req_list[1].substitute(file_name = "<br>".join(file_name))

        if not self.command_block_file_syntax : self.result_command_block_file_req = self.req_list[0].substitute()
        else :
            temp1_list = []
            for file_path in self.command_block_file_syntax : 
                for syntax in self.command_block_file_syntax[file_path] :
                    temp1_list.append(self.req_list[2].substitute(
                        file_path = file_path,
                        version = syntax[1],
                        lines = syntax[0],
                        command = syntax[2],
                        respone = syntax[3]
                    ))
            self.result_command_block_file_req = "\n".join(temp1_list)

        if not self.function_file_syntax : self.result_function_file_req = self.req_list[0].substitute()
        else :
            temp1_list = []
            for file_path in self.function_file_syntax : 
                for syntax in self.function_file_syntax[file_path] :
                    temp1_list.append(self.req_list[2].substitute(
                        file_path = file_path,
                        version = syntax[1],
                        lines = syntax[0],
                        command = syntax[2],
                        respone = syntax[3]
                    ))
            self.result_function_file_req = "\n".join(temp1_list)

        return self

    def generate_html(self, world1:str, file_name:str) :
        file1 = open(os.path.join("html_output",file_name),"w+",encoding="utf-8")
        file1.write(
            Template(self.example_html).substitute(
                worldname = world1,
                command_block_file_info=self.result_command_block_file_info,
                command_block_file_req=self.result_command_block_file_req,
                function_file_info=self.result_function_file_info,
                function_file_req=self.result_function_file_req
            )
        )
        file1.close()
        if self.command_block_file_encode or self.function_file_encode or self.command_block_file_syntax or self.function_file_syntax :
            setTimeOut(1.5, lambda: webbrowser.open("http://localhost:32323/command_load.html"))


class generate_command_respones_html : 
    
    def __init__(self, all_respones) -> None:
        self.details_template = Template("""
			<details class="details_1" id="gametick_$tick"><summary>第$tick游戏刻</summary>

				<div class="buttom_area">
					<div class="buttom" onclick="detail_class_list[$tick].add_page()">←</div>
					<div class="buttom" onclick="detail_class_list[$tick].remove_page()">→</div>
					<div style="margin: auto 10px;" id="gametick_page_info1_$tick">第1234页<br>共1234页</div>
					<input type="text" class="jump_page" id="gametick_input1_$tick" placeholder="跳转至"
					onkeypress="detail_class_list[$tick].set_display_page(document.getElementById(gametick_input1_$tick).value)">
				</div>
				
				$command_response

				<div class="buttom_area">
					<div class="buttom" onclick="detail_class_list[$tick].add_page()">←</div>
					<div class="buttom" onclick="detail_class_list[$tick].remove_page()">→</div>
					<div style="margin: auto 10px;" id="gametick_page_info2_$tick">第1234页<br>共1234页</div>
					<input type="text" class="jump_page" id="gametick_input2_$tick" placeholder="跳转至"
					onkeypress="detail_class_list[$tick].set_display_page(document.getElementById(gametick_input2_$tick).value)">
				</div>

			</details>
                """)# $command_response $tick
        self.function_stack = Template("""<div id="gametick_$tick->$count" class="normal_color" style="display:none;">$response</div>""")
        self.command_template = Template("""
				<div id="gametick_$tick->$count" class="$msgcolor" >
					<div style="display: flex;"><div style="width: 50%; border-right: 3px solid black;">第$count条</div><div style="width: 50%;">$types</div></div>
					<div style="border-top: 3px solid black;">$command<div style="height: 3px;"></div></div>
					<div style="border-top: 3px solid black;">$response<div style="height: 3px;"></div></div>
				</div>
                    """)# $tick $count $msgcolor $types $command $response

        self.all_respones:Dict[int,Dict[Literal["delay_command","loop_command","command_block","delay_function","loop_function","end_command"],
        Union[List[Response.Response_Template],List[Response.Response_Template],List[Response.Response_Template]]]] = all_respones
        self.types = {"delay_command":"延时命令","loop_command":"循环命令","command_block":"命令方块","function""函数"
                      "delay_function":"延时函数","loop_function":"循环函数","end_command":"结束命令"}

        self.html_detials_list:List[str] = []
        self.js_detial_class_list:List[str] = []

        html_file = open(os.path.join("main_source","bedrock_edition","command_class","trans_html","command_run.html"),"r",encoding="utf-8")
        self.example_html = html_file.read()
        html_file.close()

    def html_word_replace(self, text1:str) :
        text1 = text1.replace(" ","&nbsp;")
        text1 = text1.replace("<","&#60;")
        text1 = text1.replace(">","&#62;")
        text1 = text1.replace("\n","<br>")
        return text1

    def mcfunction_respones_reader(self, detial_list:list, response_1:Response.Response_Template, test_tick:int, command_counter:int) :
        respones_list:List[Union[Response.Response_Template,Response.Function_Response_Group]] = response_1.Function_Feedback[::-1]
        function_out_stack:List[int] = [response_1.Function_Feedback[::-1][0]]
        while respones_list :
            template_or_group = respones_list.pop()
            if isinstance(template_or_group, Response.Response_Template) : 
                detial_list.append( self.command_template.substitute(
                    tick = test_tick,
                    count = command_counter,
                    msgcolor = "success_color" if template_or_group.success_count else "error_color",
                    types = self.types["function"],
                    command = self.html_word_replace(template_or_group.command),
                    response = self.html_word_replace(template_or_group.command_msg)
                ))
                if template_or_group.Function_Feedback == None : continue
                respones_list.extend(template_or_group.Function_Feedback[::-1])
            elif isinstance(template_or_group, Response.Function_Response_Group) : 
                detial_list.append( self.function_stack.substitute(
                    tick = test_tick,
                    count = command_counter,
                    response = self.html_word_replace(template_or_group.push_context())
                ))
                command_counter += 1
                extend_response = template_or_group.Response_List[::-1]
                function_out_stack.append(id(extend_response[0]))
                respones_list.extend(extend_response)
            if id(template_or_group) == function_out_stack[-1] :
                detial_list.append( self.function_stack.substitute(
                    tick = test_tick,
                    count = command_counter,
                    response = self.html_word_replace(template_or_group.pop_context())
                ))
                function_out_stack.pop()
        return command_counter

    def load_all_response(self) :
        self.html_detials_list.clear() ; self.js_detial_class_list.clear()
        test_tick_min = min(list(self.all_respones)) ; single_detial_msg:List[str] = []
        for test_tick,respones_type in itertools.product(list(self.all_respones), list(self.types)) :
            command_counter = 0 ; test_tick = test_tick - test_tick_min ; single_detial_msg.clear()
            for response in self.all_respones[test_tick][respones_type] :
                single_detial_msg.append( self.command_template.substitute(
                    tick = test_tick,
                    count = command_counter,
                    msgcolor = "success_color" if response.success_count else "error_color",
                    types = self.types[respones_type],
                    command = self.html_word_replace(response.command),
                    response = self.html_word_replace(response.command_msg)
                ))
                command_counter += 1
                if response.Function_Feedback == None : continue
                command_counter = self.mcfunction_respones_reader(single_detial_msg, response, test_tick, command_counter)
            self.html_detials_list.append(self.details_template.substitute(tick=test_tick, command_response="\n".join(single_detial_msg)))
            self.js_detial_class_list.append("new detail_class(%s,%s)" % (test_tick, command_counter))


    def generate_html(self, world1:str, file_name:str) :
        file1 = open(os.path.join("html_output",file_name),"w+",encoding="utf-8")
        file1.write(Template(self.example_html).substitute(
            worldname = world1,
            all_command_respones="\n".join(self.html_detials_list),
            details_class = ",".join(self.js_detial_class_list),
        ))
        file1.close()





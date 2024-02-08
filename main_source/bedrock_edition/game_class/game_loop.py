import re,random,time,functools,webbrowser,threading
from .. import np,BaseNbtClass,Constants
from . import RunTime
from typing import List,Dict,Union,Literal,Tuple,Callable,Generator

DIMENSION_LIST = list(Constants.DIMENSION_INFO)
KEYWORD_END = re.compile("[ ]{0,}(e|E)(n|N)(d|D)[ ]{0,}$")
KEYWORD_PASS = (re.compile("[ ]{0,}(p|P)(a|A)(s|S)(s|S)[ ]{0,}"), re.compile("[0-9]{1,}[ ]{0,}$"))
KEYWORD_COMMENTARY = re.compile("//")
KEYWORD_TERMINAL_COMMAND = re.compile("[ ]{0,}#")

RUN_TERMINAL_END:Dict[int,Callable] = {}
RUN_TEST_END:Dict[int,Callable] = {}
RUN_TICK_END:Dict[int,Callable] = {}
ASYNC_FUNCTION:List[Union[Callable,Generator]] = []


class runing_command_block_obj:

    DIM = "overworld"  # Dimension where the command block is in
    ID_REDSTONE_BLOCK = 43  # Block id of Redstone Block
    ID_CB_OFFSET = 7  # Offset of block id of Command Blocks

    # CB Types
    CB_PULSE = 0
    CB_CHAIN = 1
    CB_REPEATING = 2

    # Block facing
    DOWN, UP, NORTH, SOUTH, WEST, EAST = range(6)
    FACING_OPPOSITE = {
        DOWN: UP, UP: DOWN, NORTH: SOUTH, SOUTH: NORTH, WEST: EAST, EAST: WEST
    }
    FACING2OFFSET = {
        DOWN: (0, -1, 0), UP: (0, 1, 0),
        NORTH: (0, 0, -1), SOUTH: (0, 0, 1),
        WEST: (-1, 0, 0), EAST: (1, 0, 0)
    }
    OFFSETS = tuple(FACING2OFFSET.values())

    executed_count = 0  # Number of CBs executed

    # Rule of schedule:
    # Every elements in runtime_variable.command_block_schedules is a `list`
    # with 2 elements. The first element is the block position.
    # The second element is how many ticks left until the command runs.

    def __init__(self, game_process1:RunTime.minecraft_thread) :
        self.game_process = game_process1  # minecraft_thread
        self.cb_to_run: List[Tuple[int, int, int]] = []
        self.last_activated_nbt_update: Dict[Tuple[int, int, int], bool] = {}

    @property
    def cb_schedules(self) -> List[list]:
        return self.game_process.runtime_variable.command_block_schedules

    @property
    def mc_chunk(self) -> BaseNbtClass.chunk_nbt:
        return self.game_process.minecraft_chunk

    def main(self):
        """Entry of the program."""
        for schedule in self.cb_schedules.copy():
            self.schedule_tick(schedule)
        for pos in self.mc_chunk.purple_and_orange_command_block.copy():
            ret = self.load(pos)
            if ret is True:
                self.cb_to_run.append(pos)
            elif isinstance(ret, list):
                self.cb_schedules.append(ret)
        # `load` and `schedule_tick` will tell us what CBs to run and
        # put them in `self.cb_to_run`.
        for pos in self.cb_to_run:
            self.run(pos)
        for pos, value in self.last_activated_nbt_update.items():
            try:
                _, _, _, nbt = self.get_cb_data(pos)
            except ValueError:
                continue
            nbt["LastTickActivated"] = value

    def apply_offset(self, pos, offset) -> Tuple[int, int, int]:
        """
        Return `pos` affected by `offset`.
        >>> apply_offset((10, 20, -1), (2, 0, 1))
        (12, 20, 0)
        """
        return tuple(map(sum, zip(pos, offset)))

    def get_cb_data(self, pos):
        """Return data of CB"""
        block_id = self.mc_chunk.____find_block____(self.DIM, pos)
        nbt = self.mc_chunk.____find_block_nbt____(self.DIM, pos)
        i = block_id - self.ID_CB_OFFSET
        if not (0 <= i <= 35):
            raise ValueError  # Block at `pos` is not CB now
        cb_type = i // 12
        cb_direction = i % 6
        cb_conditional = bool(i // 6 % 2)
        return (cb_type, cb_direction, cb_conditional, nbt)

    def has_schedule(self, pos) -> bool:
        """Return whether CB has a schedule"""
        for pos_got, _ in self.cb_schedules:
            if pos_got == pos:
                return True
        return False

    def can_activate(self, pos, cb_auto) -> bool:
        """Return whether CB can be activated"""
        if cb_auto:
            return True
        else:
            # Check if there is any Redstone Block around it
            for offset in self.OFFSETS:
                check_pos = self.apply_offset(pos, offset)
                if not (1600 <= check_pos[0] <= 1695 and
                        -64 <= check_pos[1] <= 319 and
                        1600 <= check_pos[2] <= 1695):
                    continue  # Redstone Block out of range
                if (self.mc_chunk.____find_block____(self.DIM, check_pos)
                    == self.ID_REDSTONE_BLOCK):
                    return True
            return False

    def load(self, pos) -> Union[list, bool]:
        """
        Load CB at `pos`.
        Return list, True or False. When False is returned, the CB should
        not be executed. When True is returned, the CB should be ran in
        this tick. When a list is returned, it is referring to a schedule,
        so the CB should be executed when the schedule fires.
        """
        try:
            cb_type, _, _, nbt = self.get_cb_data(pos)
        except ValueError:
            return False  # Not a CB at `pos`
        cb_auto = nbt["auto"]
        cb_delay = nbt["TickDelay"]
        # Check schedule for repeating CBs
        if cb_type == self.CB_REPEATING and self.has_schedule(pos):
            return False
        # Decide whether it can run
        activate = self.can_activate(pos, cb_auto)
        if cb_type == self.CB_PULSE:
            can_run = activate and (not nbt["LastTickActivated"])
            self.last_activated_nbt_update[pos] = activate
        else:  # REPEATING or CHAIN
            can_run = activate
        # Run if `can_run`
        if can_run:
            if cb_delay <= 0:
                return True  # Run in this tick
            else:
                return [pos, cb_delay]  # Schedule
        return False

    def run(self, pos) -> None:
        """Run the CB and the subsequent chain CBs."""
        cur = pos
        load_successful = True
        while True:
            try: _, cb_direction, cb_conditional, nbt = self.get_cb_data(cur)
            except ValueError: break  # Not a CB at `cur`
            cb_last_exe = nbt["LastExecution"]
            cb_command = nbt["Command"]
            # Check limit
            if self.executed_count >= self.game_process.minecraft_world.maxcommandchainlength:
                return
            if cb_last_exe == self.game_process.minecraft_world.game_time:
                return
            # Decide if we can run the command
            if load_successful:
                if cb_conditional:
                    opposite_offset = self.FACING2OFFSET[self.FACING_OPPOSITE[cb_direction]]
                    check_pos = self.apply_offset(cur, opposite_offset)
                    try: _, _, _, opposite_nbt = self.get_cb_data(check_pos)
                    except ValueError: condition_ok = False # Not a CB at `check_pos`
                    else: condition_ok = opposite_nbt["Success"]
                else : condition_ok = True
            else : condition_ok = False
            # Run command
            if condition_ok:
                if cb_command not in self.mc_chunk.command_block_compile_function : continue
                func = self.mc_chunk.command_block_compile_function[cb_command]
                response = func({
                    "executer": "command_block",
                    "dimension": self.DIM,
                    # 需要填入命令方块的坐标,给xyz都加0.5
                    "pos": [cur[0]+0.5, cur[1]+0.5, cur[2]+0.5],
                    "rotate": [0.0, 0.0],
                    "version": self.game_process.game_version
                }, self.game_process)
                self.game_process.register_response(
                    "command_block", cb_command, response
                )
                nbt["Success"] = bool(response.success_count)
                nbt["LastExecution"] = self.game_process.minecraft_world.game_time
                # print("run %d %r success=%s" % (
                #     self.game_process.minecraft_world.game_time,
                #     cb_command, response.success_count
                # ))
                self.executed_count += 1
            # Try to trigger the pointing chain CB
            next_pos = self.apply_offset(cur, self.FACING2OFFSET[cb_direction])
            try: next_cb_type, _, _, _ = self.get_cb_data(next_pos)
            except ValueError: break  # The next block is not CB, pass
            else:
                if next_cb_type == self.CB_CHAIN:
                    ret = self.load(next_pos)
                    if ret is True:
                        cur = next_pos
                        load_successful = True
                    elif isinstance(ret, list):
                        self.cb_schedules.append(ret)
                        break
                    elif ret is None:
                        cur = next_pos
                        load_successful = False

    def schedule_tick(self, schedule) -> None:
        """Runs every tick for every schedules"""
        pos = schedule[0]
        try:
            _, _, _, nbt = self.get_cb_data(pos)
        except ValueError:
            # If it is not a CB here, delete the schedule
            self.cb_schedules.remove(schedule)
            return
        cb_auto = nbt["auto"]
        if not self.can_activate(pos, cb_auto):
            self.cb_schedules.remove(schedule)
            return
        schedule[1] -= 1
        if schedule[1] == 0:
            self.cb_to_run.append(pos)
            self.cb_schedules.remove(schedule)



def game_time_tick(self:RunTime.minecraft_thread) :
    self.minecraft_world.game_time += 1
    gt1 = str(self.minecraft_world.game_time)
    if self.minecraft_world.dodaylightcycle : self.minecraft_world.day_count += np.int32(1)
    self.minecraft_world.day_time = self.minecraft_world.day_count // 24000
    if self.minecraft_world.doweathercycle :
        if self.minecraft_world.sunny_time > 0 : self.minecraft_world.sunny_time -= 1
        if self.minecraft_world.rain_time > 0 : self.minecraft_world.rain_time -= 1
        if self.minecraft_world.thunder_time > 0 : self.minecraft_world.thunder_time -= 1
        if (self.minecraft_world.sunny_time <= 0 and self.minecraft_world.rain_time <= 0 and
            self.minecraft_world.thunder_time <= 0) :
            list1 = [random.randint(60000,100000),0,0]
            random.shuffle(list1)
            self.minecraft_world.sunny_time = np.int32(list1[0])
            self.minecraft_world.rain_time = np.int32(list1[1])
            self.minecraft_world.thunder_time = np.int32(list1[2])
    
    if gt1 in self.runtime_variable.scoreboard_score_remove :
        for name in self.runtime_variable.scoreboard_score_remove[gt1] : self.minecraft_scoreboard.__reset_score__((name,))
        del self.runtime_variable.scoreboard_score_remove[gt1]

def loading_chunk(self:RunTime.minecraft_thread) :
    self.minecraft_chunk.out_load_entity.clear()

    self.minecraft_chunk.____load_chunk_data____(self.minecraft_world, self.world_name, self.minecraft_world.simulator_distance)
    self.minecraft_chunk.____save_outload_chunk_data____(self.world_name)
    if self.minecraft_world.game_time % 5000 == 0 : self.minecraft_chunk.____save_and_write_db_file____(self.world_name)
    self.game_load_over = True

def player_things(self:RunTime.minecraft_thread) :
    for player1 in self.minecraft_chunk.player :
        if player1.RespawnTime == 1 and player1.Health <= 0 :
            try : player1.Health = player1.Attributes['max_health']['Base']
            except : player1.Health = np.float32(20)
            player1.Pos[0] = player1.SpawnPoint[0]
            player1.Pos[1] = player1.SpawnPoint[1]
            player1.Pos[2] = player1.SpawnPoint[2]
        if player1.RespawnTime > 0 : player1.RespawnTime -= 1
        if player1.Health <= 0 and player1.RespawnTime <= 0 and self.minecraft_world.doimmediaterespawn : player1.RespawnTime = 5
        if player1.Health <= 0 and player1.RespawnTime <= 0 and (not self.minecraft_world.doimmediaterespawn) : player1.RespawnTime = 100
        if player1.damage['time_no_hurt'] == 1 : player1.damage['value'] = 0
        if player1.damage['time_no_hurt'] > 0 : player1.damage['time_no_hurt'] -= 1
        
        if player1.SelectSlot > len(player1.HotBar) : player1.SelectSlot = 0
        player1.Weapon[0] = player1.HotBar[player1.SelectSlot]
        player1.__update_mainhand__()

def entity_things(self:RunTime.minecraft_thread) :
    entity_list = self.minecraft_chunk.__get_all_load_entity__()
    for entity1 in entity_list :

        if (self.minecraft_world.difficulty == 0) and ("monster" in entity1.FamilyType) : 
            self.minecraft_chunk.__remove_entity__(entity1, scoreboard_obj=self.minecraft_scoreboard)

        if (entity1.Identifier == "minecraft:player") and (entity1.Health <= 0) : 
            self.minecraft_chunk.__add_entity__(*entity1.__sit_evict_riders__())
            entity1.__sit_stop_riding__(entity_list)

        if hasattr(entity1, "Health") and (entity1.Identifier != "minecraft:player") and (entity1.Health <= 0) : 
            time = str(self.minecraft_world.game_time + 5)
            if time not in self.runtime_variable.scoreboard_score_remove : self.runtime_variable.scoreboard_score_remove[time] = []
            self.runtime_variable.scoreboard_score_remove[time].append(entity1)
            self.minecraft_chunk.__add_entity__(*entity1.__sit_evict_riders__())
            if entity1.__sit_stop_riding__(entity_list) : pass
            else : self.minecraft_chunk.__remove_entity__(entity1)
            continue

        if entity1.damage['time_no_hurt'] == 1 : entity1.damage['value'] = 0
        if entity1.damage['time_no_hurt'] > 0 : entity1.damage['time_no_hurt'] -= 1

        if hasattr(entity1,"ActiveEffects") :
            for effect1 in list(entity1.ActiveEffects) :
                if entity1.ActiveEffects[effect1]["Duration"] < 1 : del entity1.ActiveEffects[effect1]
                elif entity1.ActiveEffects[effect1]["Duration"] > 0 : entity1.ActiveEffects[effect1]["Duration"] -= 1

        entity1.__sit_update__(self.minecraft_chunk.player)

def terminal_running(self:RunTime.minecraft_thread) :
    from .. import Command_Tokenizer_Compiler,TerminalCommand
    if not self.runtime_variable.terminal_send_command : return None
    self.runtime_variable.terminal_clear()

    executer = self.minecraft_chunk.player[0]
    context = {"executer":executer,"dimension":DIMENSION_LIST[executer.Dimension],"pos":list(executer.Pos),
               "rotate":list(executer.Rotation),"version":self.game_version}

    feedback_list = self.runtime_variable.terminal_command_feedback
    pass_times = 0 ; command_function:List[Tuple[str,functools.partial]] = []
    for lines,command_text in enumerate(self.runtime_variable.terminal_command.split("\n")) : 
        lines = lines + 1
        if command_text.replace(" ","") == "" : continue
        elif KEYWORD_END.match(command_text) : break #关键字
        elif pass_times : pass_times -= 1 ; continue
        elif KEYWORD_PASS[0].match(command_text) : #关键字
            keyword_end = KEYWORD_PASS[0].match(command_text).end()
            times = KEYWORD_PASS[1].search(command_text, keyword_end)
            mid1 = int(0 if times is None else times.group())
            if mid1 < 1 : feedback_list.append((lines, "pass 的参数应该为正整数", keyword_end)) ; continue
            pass_times = mid1
        elif KEYWORD_COMMENTARY.match(command_text) : continue
        elif KEYWORD_TERMINAL_COMMAND.match(command_text) : 
            a = TerminalCommand.Terminal_Compiler(self,command_text)
            if isinstance(a, Exception) : feedback_list.append((lines, a.args[0], a.pos[0] if hasattr(a,"pos") else 0))
            else : 
                command_function.append( (command_text,a) )
                if id(a.func) == id(TerminalCommand.set_version) : a(context, self)
        else :
            func_object = Command_Tokenizer_Compiler(self, command_text, self.game_version)
            if isinstance(func_object, tuple) : 
                feedback_list.append( (lines, func_object[0], func_object[1].pos[0] if hasattr(func_object[1],"pos") else 0) )
                continue
            command_function.append( (command_text,func_object) )

    if len(feedback_list) == 0 :
        for command,function in command_function : 
            try : feedback = function(context, self)
            except Exception as e : print(command, function) ; raise e
            else : feedback_list.append( feedback.set_command(command) )

    #print(debug_windows.terminal_log) "[\u2714]" "[\u2718]"
    termial_end_hook(self)
    if self.visualization_object : 
        self.visualization_object.first_get_ready = True
        self.visualization_object.save_a_test_data()
    self.runtime_variable.terminal_send_command = False

#

def command_running(self:RunTime.minecraft_thread) :
    if self.runtime_variable.how_times_run_all_command <= 0 : return None
    aaa = {"executer":"server","dimension":"overworld","pos":[0,0,0],"rotate":[0,0],"version":self.game_version}
    if self.minecraft_world.game_time in self.runtime_variable.command_will_run :
        for command_str,func in self.runtime_variable.command_will_run[self.minecraft_world.game_time] :
            self.register_response("delay_command",command_str,func(aaa, self))

    for command_str,func in self.runtime_variable.command_will_loop : self.register_response("loop_command",command_str,func(aaa, self))

def command_block_running(self:RunTime.minecraft_thread) :
    if self.runtime_variable.how_times_run_all_command <= 0 : return None
    if not self.minecraft_world.commandblocksenabled : return None
    run_cb_obj = runing_command_block_obj(self)
    run_cb_obj.main()

def particle_alive(self:RunTime.minecraft_thread) :
    for i in self.runtime_variable.particle_alive :
        now_time = self.minecraft_world.game_time.__str__()
        if now_time not in self.runtime_variable.particle_alive[i] : continue
        del self.runtime_variable.particle_alive[i][now_time]

def command_run_end(self:RunTime.minecraft_thread) :
    from .. import HtmlGenerate
    if self.runtime_variable.how_times_run_all_command > 0 and self.visualization_object : 
        self.visualization_object.save_a_test_data()

    if self.runtime_variable.how_times_run_all_command == 0 :
        aaa = {"executer":"server","execute_dimension":"overworld","execute_pos":[0,0,0],"execute_rotate":[0,0],"version":self.game_version}
        for command_str,func in self.runtime_variable.command_will_run_test_end : 
            self.register_response("end_command", command_str, func(aaa, self))

        test_end_hook(self)

        if self.runtime_variable.all_command_response.__len__() :
            a = HtmlGenerate.generate_command_respones_html(self.runtime_variable.all_command_response)
            a.load_all_response()
            a.generate_html(self.world_name, "command_respones.html")
            if self.runtime_variable.open_response_website : 
                threading.Thread(lambda:[time.sleep(1.5), webbrowser.open("http://localhost:32323/command_respones.html")]).start()

        if self.visualization_object : self.visualization_object.set_test_end_flag()
    
    if self.runtime_variable.how_times_run_all_command >= 0 :
        self.runtime_variable.how_times_run_all_command -= 1



def termial_end_hook(self:RunTime.minecraft_thread) :
    for func in list(RUN_TERMINAL_END.values()) : func(self)

def test_end_hook(self:RunTime.minecraft_thread) :
    for func in list(RUN_TEST_END.values()) : func(self)

def tick_end_hook(self:RunTime.minecraft_thread) :
    for func in list(RUN_TICK_END.values()) : func(self)

def async_run(self:RunTime.minecraft_thread) :
    for func in list(ASYNC_FUNCTION) : 
        if func() == "end" : ASYNC_FUNCTION.remove(func)

def modify_termial_end_hook(mode:Literal["add","remove","clear"]="add", _func:Callable=None) :
    if mode in ("add","remove") and not hasattr(_func, "__call__") : return
    if _func : dict_key = _func.__code__.co_code.__hash__()
    if mode == "add" : RUN_TERMINAL_END[dict_key] = _func
    elif mode == "remove" and dict_key in RUN_TERMINAL_END : del RUN_TERMINAL_END[dict_key]
    elif mode == "clear" : RUN_TERMINAL_END.clear()

def modify_test_end_hook(mode:Literal["add","remove","clear"]="add", _func:Callable=None) :
    if mode in ("add","remove") and not hasattr(_func, "__call__") : return
    if _func : dict_key = _func.__code__.co_code.__hash__()
    if mode == "add" : RUN_TEST_END[dict_key] = _func
    elif mode == "remove" and dict_key in RUN_TEST_END : del RUN_TEST_END[dict_key]
    elif mode == "clear" : RUN_TEST_END.clear()

def modify_tick_end_hook(mode:Literal["add","remove","clear"]="add", _func:Callable=None) :
    if mode in ("add","remove") and not hasattr(_func, "__call__") : return
    if _func : dict_key = _func.__code__.co_code.__hash__()
    if mode == "add" : RUN_TICK_END[dict_key] = _func
    elif mode == "remove" and dict_key in RUN_TICK_END : del RUN_TICK_END[dict_key]
    elif mode == "clear" : RUN_TICK_END.clear()

def modify_async_func(mode:Literal["add","clear"]="add", _func:Callable=None) :
    if mode in ("add") and (not hasattr(_func, "__call__") and not hasattr(_func, "__next__")) : return
    if mode == "add" : ASYNC_FUNCTION.append(_func)
    elif mode == "clear" : ASYNC_FUNCTION.clear()


loop_function_list = [
    game_time_tick, loading_chunk, player_things, entity_things, async_run, terminal_running,
    command_running, command_block_running, particle_alive, command_run_end, tick_end_hook
]







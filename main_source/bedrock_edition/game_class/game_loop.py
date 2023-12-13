import re,random,math,functools
from .. import np,BaseNbtClass,Constants
from . import RunTime
from typing import List,Dict,Union,Literal,Tuple,Callable

DIMENSION_LIST = list(Constants.DIMENSION_INFO)
KEYWORD_END = re.compile("[ ]{0,}(e|E)(n|N)(d|D)[ ]{0,}$")
KEYWORD_PASS = (re.compile("[ ]{0,}(p|P)(a|A)(s|S)(s|S)[ ]{0,}"), re.compile("[0-9]{1,}[ ]{0,}$"))
KEYWORD_COMMENTARY = re.compile("//")
KEYWORD_TERMINAL_COMMAND = re.compile("[ ]{0,}#")

RUN_TERMINAL_END:Dict[int,Callable] = {}
RUN_TEST_END:Dict[int,Callable] = {}
RUN_TICK_END:Dict[int,Callable] = {}



class runing_command_block_obj:

    DIM = "overworld" # Dimension where the command block is in
    ID_REDSTONE_BLOCK = 43 # Block id of Redstone Block
    ID_CB_OFFSET = 7 # Offset of block id of Command Blocks

    # CB Types
    CB_PULSE = 0
    CB_CHAIN = 1
    CB_REPEATING = 2

    # Block facing
    DOWN, UP, NORTH, SOUTH, WEST, EAST = tuple(range(6))
    FACING_OPPOSITE = {
        DOWN: UP, UP: DOWN, NORTH: SOUTH, SOUTH: NORTH, WEST: EAST, EAST: WEST
    }
    FACING2OFFSET = {
        DOWN: (0, -1, 0), UP: (0, 1, 0),
        NORTH: (0, 0, -1), SOUTH: (0, 0, 1),
        WEST: (-1, 0, 0), EAST: (1, 0, 0)
    }
    OFFSETS = tuple(FACING2OFFSET.values())

    executed_count = 0 # How many CBs have been executed

    # Rule of schedule:
    # Every elements in running_object.command_block_schedules is a `list`
    # with 2 elements. The first element is the block position.
    # The second element is how many ticks left until the command runs

    def __init__(self,game_process1,debug_windows1) :
        self.game_process = game_process1
        self.debug_windows = debug_windows1
        self.cb_to_run = []
        # last_activated_nbt_update: {tuple: bool} tuple is pos, bool is value
        self.last_activated_nbt_update = {}
    
    def main(self):
        """Entry of the program."""
        for schedule in self.game_process.command_block_schedules.copy():
            self.schedule_tick(schedule)
        for pos in self.game_process.purple_and_orange_command_block.copy():
            ret = self.load(pos)
            if ret is True:
                self.cb_to_run.append(pos)
            elif isinstance(ret, list):
                self.game_process.command_block_schedules.append(ret)
        # load and schedule_tick will filter which CBs can be ran, and store
        # the pos of those CBs which can run in `self.cb_to_run`
        for pos in self.cb_to_run:
            self.run(pos)
        for pos, value in self.last_activated_nbt_update.items():
            try:
                _, _, _, nbt = self.get_cb_data(pos)
            except ValueError:
                continue
            nbt["LastTickActivated"] = value

    def apply_offset(self,pos, offset) -> tuple:
        """
        Return `pos` affected by `offset`.
        >>> apply_offset((10, 20, -1), (2, 0, 1))
        (12, 20, 0)
        """
        return tuple(map(sum, zip(pos, offset)))

    def get_cb_data(self,pos):
        """Return data of CB"""
        block_id = self.game_process.minecraft_chunk.____find_chunk_block_2____(pos, self.DIM)
        nbt = self.game_process.minecraft_chunk.____find_chunk_block_nbt_2____(pos, self.DIM)
        i = block_id - self.ID_CB_OFFSET
        if not (0 <= i <= 35):
            raise ValueError # Block at `pos` is not CB now
        cb_type = i // 12
        cb_direction = i % 6
        cb_conditional = bool(i // 6 % 2)
        return (cb_type, cb_direction, cb_conditional, nbt)

    def has_schedule(self,pos) -> bool:
        """Return whether CB has a schedule"""
        for schedule in self.game_process.command_block_schedules:
            if schedule[0] == pos:
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
                    continue # Redstone Block out of range
                if self.game_process.minecraft_chunk.____find_chunk_block_2____(
                    check_pos, self.DIM
                ) == self.ID_REDSTONE_BLOCK:
                    return True
            return False

    def load(self, pos):
        """
        Load CB at `pos`.
        Return list, True or None. When None is returned, the CB should
        not be executed. When True is returned, the CB should be ran in
        this tick. When a list is returned, it is referring to a schedule,
        so the CB should be executed when the schedule fires.
        """
        try:
            cb_type, _, _, nbt = self.get_cb_data(pos)
        except ValueError:
            return # Not a CB at `pos`
        cb_auto = nbt["auto"]
        cb_delay = nbt["TickDelay"]
        # Check schedule for repeating CBs
        if cb_type == self.CB_REPEATING and self.has_schedule(pos):
            return
        # Decide whether it can run
        activate = self.can_activate(pos, cb_auto)
        if cb_type == self.CB_PULSE:
            can_run = False
            if activate and (not nbt["LastTickActivated"]):
                can_run = True
            self.last_activated_nbt_update[pos] = activate
        else: # REPEATING or CHAIN
            can_run = activate
        # Run if `can_run`
        if can_run:
            if cb_delay <= 0:
                return True # Run in this tick
            else:
                return [pos, cb_delay] # Schedule

    def run(self,pos):
        """Run the CB and the chained CBs to it."""
        cur = pos
        load_successful = True
        while True:
            try:
                _, cb_direction, cb_conditional, nbt = self.get_cb_data(cur)
            except ValueError:
                break # Not a CB at `cur`
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
                    try:
                        _, _, _, opposite_nbt = self.get_cb_data(check_pos)
                    except ValueError: # Not a CB at `check_pos`
                        condition_ok = False
                    else:
                        condition_ok = opposite_nbt["Success"]
                else:
                    condition_ok = True
            else:
                condition_ok = False
            # Run command
            if condition_ok:
                # execute_var['execute_pos'] 需要填入命令方块的坐标,给xyz都加0.5
                execute_var = {
                    "executer": "command_block",
                    "execute_dimension": self.DIM,
                    "execute_pos": [cur[0]+0.5,cur[1]+0.5,cur[2]+0.5],
                    "execute_rotate": [0, 0]
                }
                if cb_command.replace(" ","") and cb_command.replace(" ","")[0] == "#" : 
                    response = self.game_process.debug_command.intro(execute_var,cb_command)
                else :
                    response = self.game_process.command_system.intro(self.game_process.game_command_version,execute_var,cb_command)
                self.game_process.be_register_response(("command_block",cb_command,response))
                #print("Tick %d: %s" % (self.game_process.minecraft_world.game_time, response))

                nbt["Success"] = bool(response.success_count)
                nbt["LastExecution"] = self.game_process.minecraft_world.game_time
                self.executed_count += 1
            # Try to trigger the pointing chain CB
            pointing_offset = self.FACING2OFFSET[cb_direction]
            point_pos = self.apply_offset(cur, pointing_offset)
            try:
                point_cb_type, _, _, _ = self.get_cb_data(point_pos)
            except ValueError:
                break # The pointing block is not CB, pass
            else:
                if point_cb_type == self.CB_CHAIN:
                    ret = self.load(point_pos)
                    if ret is True:
                        cur = point_pos
                        load_successful = True
                    elif isinstance(ret, list):
                        self.game_process.command_block_schedules.append(ret)
                        break
                    elif ret is None:
                        cur = point_pos
                        load_successful = False

    def schedule_tick(self,schedule):
        """Runs every tick for every schedules"""
        pos = schedule[0]
        try:
            _, _, _, nbt = self.get_cb_data(pos)
        except ValueError:
            # If it is not a CB here, delete the schedule
            self.game_process.command_block_schedules.remove(schedule)
            return
        cb_auto = nbt["auto"]
        if not self.can_activate(pos, cb_auto):
            self.game_process.command_block_schedules.remove(schedule)
            return
        
        schedule[1] -= 1
        if schedule[1] == 0:
            self.cb_to_run.append(pos)
            self.game_process.command_block_schedules.remove(schedule)



def remove_entity(game:RunTime.minecraft_thread, *entity_list:BaseNbtClass.entity_nbt) :
    for entity1 in entity_list :
        chunk_pos = (math.floor(entity1.Pos[0])//16*16, math.floor(entity1.Pos[2])//16*16)
        entity_chunk_list = game.minecraft_chunk.loading_chunk[DIMENSION_LIST[entity1.Dimension]][chunk_pos]["entities"]
        if entity1 in entity_chunk_list : entity_chunk_list.remove(entity1)

def add_entity(game:RunTime.minecraft_thread, *entity_list:BaseNbtClass.entity_nbt) :
    for entity1 in entity_list :
        chunk_pos = (math.floor(entity1.Pos[0])//16*16, math.floor(entity1.Pos[2])//16*16)
        entity_chunk_list = game.minecraft_chunk.loading_chunk[DIMENSION_LIST[entity1.Dimension]][chunk_pos]["entities"]
        if entity1 in entity_chunk_list : entity_chunk_list.append(entity1)



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
        for name in self.runtime_variable.scoreboard_score_remove[gt1] : self.minecraft_scoreboard.__reset_score__(name)
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

def entity_things(self:RunTime.minecraft_thread) :
    entity_list = self.minecraft_chunk.__get_all_load_entity__()
    for entity1 in entity_list :

        if (self.minecraft_world.difficulty == 0) and ("monster" in entity1.FamilyType) : remove_entity(self, entity1)

        if (entity1.Identifier == "minecraft:player") and (entity1.Health <= 0) : 
            add_entity(self, *entity1.__sit_evict_riders__())
            entity1.__sit_stop_riding__(entity_list)

        if hasattr(entity1,"Health") and (entity1.Identifier != "minecraft:player") and (entity1.Health <= 0) : 
            time = str(self.minecraft_world.game_time + 5)
            if time not in self.runtime_variable.scoreboard_score_remove : self.runtime_variable.scoreboard_score_remove[time] = []
            self.runtime_variable.scoreboard_score_remove[time].append(entity1)
            add_entity(self, *entity1.__sit_evict_riders__())
            entity1.__sit_stop_riding__(entity_list)
            remove_entity(self, entity1)
            continue

        if entity1.damage['time_no_hurt'] == 1 : entity1.damage['value'] = 0
        if entity1.damage['time_no_hurt'] > 0 : entity1.damage['time_no_hurt'] -= 1

        if hasattr(entity1,"CustomEffects") :
            for effect1 in entity1.CustomEffects :
                if entity1.CustomEffects[effect1]["Duration"] < 1 : del entity1.CustomEffects[effect1]
                elif entity1.CustomEffects[effect1]["Duration"] > 0 : entity1.CustomEffects[effect1]["Duration"] -= 1

        entity1.__sit_update__()

def terminal_running(self:RunTime.minecraft_thread) :
    from .. import CommandParser,CommandCompiler,TerminalCommand
    if not self.runtime_variable.terminal_send_command : return None
    self.runtime_variable.terminal_clear()

    executer = self.minecraft_chunk.player[0]
    context = {"executer":executer,"dimension":DIMENSION_LIST[executer.Dimension],"pos":executer.Pos,"rotate":executer.Rotation}

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
            mid1 = int(0 if times == None else times)
            if mid1 < 1 : feedback_list.append((lines, "pass 的参数应该为正整数", keyword_end)) ; continue
            pass_times = mid1
        elif KEYWORD_COMMENTARY.match(command_text) : continue
        elif KEYWORD_TERMINAL_COMMAND.match(command_text) : 
            a = TerminalCommand.Terminal_Compiler(command_text)
            if isinstance(a, Exception) : feedback_list.append((lines, a.args[0], a.pos[0] if hasattr(a,"pos") else 0))
            else : command_function.append( (command_text,a) )
        else :
            token_list = CommandParser.Start_Tokenizer(command_text, self.game_version)
            if isinstance(token_list, tuple) : 
                feedback_list.append( (lines, token_list[0], token_list[1].pos[0]) )
                continue
            func_object = CommandCompiler.Start_Compile(token_list, self.game_version, self)
            if isinstance(func_object, tuple) : 
                feedback_list.append( (lines, func_object[0], func_object[1].pos[0] if hasattr(func_object[1],"pos") else 0) )
                continue
            command_function.append( (command_text,func_object) )

    if len(feedback_list) == 0 :
        for command,function in command_function : 
            feedback = function(context)
            feedback_list.append( feedback.set_command(command) )

    #print(debug_windows.terminal_log) "[\u2714]" "[\u2718]"
    termial_end_hook(self)
    self.runtime_variable.terminal_send_command = False

#

def command_running(self:RunTime.minecraft_thread) :
    aaa = {"executer":"server","execute_dimension":"overworld","execute_pos":[0,0,0],"execute_rotate":[0,0],"version":self.game_version}
    if self.minecraft_world.game_time in self.runtime_variable.command_will_run :
        for command_str,func in self.runtime_variable.command_will_run[self.minecraft_world.game_time] :
            self.register_response("delay_command",command_str,func(aaa))

    for command_str,func in self.runtime_variable.command_will_loop : self.register_response("loop_command",command_str,func(aaa))

def command_block_running(self:RunTime.minecraft_thread) :
    return None
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
    if self.runtime_variable.how_times_run_all_command == 0 :
        aaa = {"executer":"server","execute_dimension":"overworld","execute_pos":[0,0,0],"execute_rotate":[0,0],"version":self.game_version}
        for command_str,func in self.runtime_variable.command_will_run_test_end : 
            self.register_response("end_command",command_str,func(aaa))

        test_end_hook(self)

        a = HtmlGenerate.generate_command_respones_html(self.runtime_variable.all_command_response)
        a.load_all_response()
        a.generate_html(self.world_name, "command_respones.html")



def termial_end_hook(self:RunTime.minecraft_thread) :
    for func in list(RUN_TERMINAL_END.values()) : func(self)

def test_end_hook(self:RunTime.minecraft_thread) :
    for func in list(RUN_TEST_END.values()) : func(self)

def tick_end_hook(self:RunTime.minecraft_thread) :
    for func in list(RUN_TICK_END.values()) : func(self)

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



loop_function_list = [
    game_time_tick, loading_chunk, player_things, entity_things, terminal_running,
    command_running, command_block_running, particle_alive, command_run_end, 
    tick_end_hook
]








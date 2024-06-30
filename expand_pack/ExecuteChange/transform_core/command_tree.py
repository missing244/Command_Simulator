from main_source.bedrock_edition.command_class.parser import SpecialMatch,BaseMatch,ParserSystem

def BE_BlockState_Tree(*end_node:BaseMatch.Match_Base) :
    """
    自动生成一个方块状态选择器匹配树\n
    ...end_node : 添加下一级匹配类\n
    """
    start1 = BaseMatch.KeyWord("Start_BlockState_Argument","[").add_leaves(
        BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node)
    )
    start2 = SpecialMatch.BE_BlockState_String("BlockState")
    start2.add_leaves(
        BaseMatch.KeyWord("Equal",":").add_leaves(
            SpecialMatch.BE_BlockState_String("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Enum("Value","true","false").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Int("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
        ),
        BaseMatch.KeyWord("Equal","=").add_leaves(
            SpecialMatch.BE_BlockState_String("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Enum("Value","true","false").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Int("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
        )
    )
    start1.add_leaves(start2)
    return start1



#exexute的旧语法
def Old_Execute(Command_Tree:BaseMatch.Match_Base) :
    aaa = BaseMatch.Char("Command","execute").set_version(1,19,50,"max")
    Command_Tree.add_leaves(aaa, BaseMatch.AnyMsg("Any_Command").add_leaves( BaseMatch.END_NODE ))

    aaa.add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            *SpecialMatch.Pos_Tree(
                BaseMatch.Char("Block_Test","detect").add_leaves(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.AnyString("Block_ID").add_leaves(
                            BaseMatch.Int("Block_Data").add_leaves( 
                                Command_Tree,
                                *Command_Tree.tree_leaves 
                            )
                        )
                    )
                ),
                Command_Tree,
                *Command_Tree.tree_leaves
            )
        )
    )

#exexute的新语法
def NewExecute(Command_Tree:BaseMatch.Match_Base) :
    aaa = BaseMatch.Char("Command","execute").set_version(1,19,50,"min")
    Command_Tree.add_leaves(aaa, BaseMatch.AnyMsg("Any_Command").add_leaves( BaseMatch.END_NODE ))

    Command_Execute = [
        BaseMatch.Char("Sub_Command","align"),
        BaseMatch.Char("Sub_Command","anchored"),
        BaseMatch.Char("Sub_Command","as"),
        BaseMatch.Char("Sub_Command","at"),
        BaseMatch.Char("Sub_Command","facing"),
        BaseMatch.Char("Sub_Command","in"),
        BaseMatch.Char("Sub_Command","positioned"),
        BaseMatch.Char("Sub_Command","rotated"),
        BaseMatch.Enum("Sub_Command","if","unless"),
        BaseMatch.Char("Sub_Command","run")
    ]
    Command_Execute[0].add_leaves(   # align
        BaseMatch.Enum("Axes","x","y","z","xy","xz","yz","yx","zx","zy","xyz","xzy","yxz","yzx","zxy","zyx").add_leaves(*Command_Execute)
    )
    Command_Execute[1].add_leaves(   # anchored
        BaseMatch.Enum("Anchor","eyes","feet").add_leaves(*Command_Execute)
    )
    Command_Execute[2].add_leaves(   # as
        *SpecialMatch.BE_Selector_Tree(*Command_Execute)
    )
    Command_Execute[3].add_leaves(   # at
        *SpecialMatch.BE_Selector_Tree(*Command_Execute)
    )
    Command_Execute[4].add_leaves(   # facing
        *SpecialMatch.Pos_Tree(*Command_Execute),
        BaseMatch.Char("Argument","entity").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.Enum("Anchor","eyes","feet").add_leaves(*Command_Execute)
            )
        )
    )
    Command_Execute[5].add_leaves(   # in
        BaseMatch.Enum("Dimension","overworld","nether","the_end").add_leaves(*Command_Execute)
    )
    Command_Execute[6].add_leaves(   # positioned
        *SpecialMatch.Pos_Tree(*Command_Execute),
        BaseMatch.Char("Argument","as").add_leaves(
            *SpecialMatch.BE_Selector_Tree(*Command_Execute)
        )
    )
    Command_Execute[7].add_leaves(   # rotated
        *SpecialMatch.Rotation_Tree(*Command_Execute),
        BaseMatch.Char("Argument","as").add_leaves(
            *SpecialMatch.BE_Selector_Tree(*Command_Execute)
        )
    )
    Command_Execute[8].add_leaves(   # if unless
        BaseMatch.Char("Type","block").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.AnyString("Block_ID").set_version(1,19,70,"min").add_leaves(
                    BE_BlockState_Tree(BaseMatch.END_NODE, *Command_Execute),
                    *Command_Execute,
                    BaseMatch.END_NODE
                ),
                BaseMatch.AnyString("Block_ID").set_version(1,19,70,"max").add_leaves(
                    BaseMatch.Int("Block_Data").add_leaves(BaseMatch.END_NODE, *Command_Execute),
                    BE_BlockState_Tree(*Command_Execute),
                    *Command_Execute,
                    BaseMatch.END_NODE
                )
            )
        ),
        BaseMatch.Char("Type","blocks").add_leaves(
            *SpecialMatch.Pos_Tree( *SpecialMatch.Pos_Tree( *SpecialMatch.Pos_Tree(
                BaseMatch.Enum("Scan_Mode","all","masked").add_leaves(BaseMatch.END_NODE, *Command_Execute)
            )))
        ),
        BaseMatch.Char("Type","entity").add_leaves(
            *SpecialMatch.BE_Selector_Tree(BaseMatch.END_NODE, *Command_Execute)
        ),
        BaseMatch.Char("Type","score").add_leaves(
            *SpecialMatch.Scoreboard_Entity_Name_Tree(
                *SpecialMatch.String_Tree("Scoreboard_Name",
                    BaseMatch.KeyWord("Operation","=","<","<=",">",">=").add_leaves(
                        *SpecialMatch.Scoreboard_Entity_Name_Tree(
                            *SpecialMatch.String_Tree("Scoreboard_Name", *Command_Execute, BaseMatch.END_NODE)
                        )
                    ),
                    BaseMatch.Char("Operation","matches").add_leaves(
                        *SpecialMatch.Range_Tree(BaseMatch.END_NODE, *Command_Execute)
                    )
                )
            )
        )
    )
    Command_Execute[9].add_leaves(   # run
        *Command_Tree.tree_leaves
    )
    aaa.add_leaves(Command_Tree, *Command_Execute)

#setblock语法
Setblock = BaseMatch.Char("Command","setblock").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.AnyString("Block_ID").add_leaves(
                    BE_BlockState_Tree( 
                        BaseMatch.Enum("Setblock_Mode","replace","keep","destroy").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.Int("Block_Data").add_leaves(
                        BaseMatch.Enum("Setblock_Mode","replace","keep","destroy").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            )
        )

Testforblock = BaseMatch.Char("Command","testforblock").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.AnyString("Block_ID").add_leaves(
                    BE_BlockState_Tree( BaseMatch.END_NODE ),
                    BaseMatch.Int("Block_Data").add_leaves( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )    
        )

Clone = BaseMatch.Char("Command","clone").add_leaves(
            *SpecialMatch.Pos_Tree(
                *SpecialMatch.Pos_Tree(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.Enum("Mask_Mode","replace","masked").add_leaves(
                            BaseMatch.Enum("Clone_Mode","force","move","normal").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.Enum("Mask_Mode:指定拷贝方块","filtered").add_leaves(
                            BaseMatch.Enum("Clone_Mode","force","move","normal").add_leaves(
                                BaseMatch.AnyString("Block_ID").add_leaves(
                                    BE_BlockState_Tree( BaseMatch.END_NODE ),
                                    BaseMatch.Int("Block_Data").add_leaves( BaseMatch.END_NODE )
                                )
                            )
                        ),
                        BaseMatch.END_NODE
                    )
                )
            )    
        )

Fill = BaseMatch.Char("Command","fill").add_leaves(
            *SpecialMatch.Pos_Tree(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.AnyString("Block_ID").add_leaves(
                        BE_BlockState_Tree( 
                            BaseMatch.Char("Fill_Mode","replace").add_leaves(
                                BaseMatch.AnyString("Block_ID").add_leaves(
                                    BE_BlockState_Tree( BaseMatch.END_NODE ),
                                    BaseMatch.END_NODE
                                ),
                                BaseMatch.END_NODE
                            ),
                            BaseMatch.Enum("Fill_Mode","hollow","keep","outline","destroy").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.Int("Block_Data").add_leaves( 
                            BaseMatch.Char("Fill_Mode","replace").add_leaves(
                                BaseMatch.AnyString("Block_ID").add_leaves(
                                    BaseMatch.Int("Block_Data").add_leaves( BaseMatch.END_NODE ),
                                    BaseMatch.END_NODE
                                ),
                                BaseMatch.END_NODE
                            ),
                            BaseMatch.Enum("Fill_Mode","hollow","keep","outline","destroy").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    )
                )
            )
        )

#summon
Summon = BaseMatch.Char("Command","summon").set_version(1,19,70,"max").add_leaves(
            BaseMatch.AnyString("Entity_Type").add_leaves(
                *SpecialMatch.Pos_Tree(
                    *SpecialMatch.String_Tree("Entity_Event",
                        *SpecialMatch.String_Tree( "Entity_Name", BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                *SpecialMatch.String_Tree("Entity_Name",
                    *SpecialMatch.Pos_Tree( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            )
        )

#structure
Command_Structure = BaseMatch.Enum("Include_Entities","true","false").add_leaves(
    BaseMatch.Enum("Include_Blocks","true","false").add_leaves(
        BaseMatch.Float("Integrity").add_leaves(
            SpecialMatch.BE_Quotation_String("Seed").add_leaves( BaseMatch.END_NODE ),
            SpecialMatch.BE_String("Seed").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        ),
        BaseMatch.END_NODE
    ),
    BaseMatch.END_NODE
)
Structure = BaseMatch.Char("Command","structure").set_version(1,19,30,"max").add_leaves(
        BaseMatch.Char("Model","save").add_leaves(
            *SpecialMatch.String_Tree("Structure_Name",
                *SpecialMatch.Pos_Tree(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.Enum("Save_Mode","memory","disk").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.Enum("IncludeEntities","true","false").add_leaves(
                            BaseMatch.Enum("Save_Mode","memory","disk").add_leaves(
                                BaseMatch.Enum("IncludeBlocks","true","false").add_leaves( BaseMatch.END_NODE ),
                                BaseMatch.END_NODE
                            ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    )
                )
            )
        ),
        BaseMatch.Char("Model","load").add_leaves(
            *SpecialMatch.String_Tree("Structure_Name",
                *SpecialMatch.Pos_Tree(
                    BaseMatch.Enum("Rotation","0_degrees","90_degrees","180_degrees","270_degrees").add_leaves(
                        BaseMatch.Enum("Mirror","none","x","z","xz").add_leaves(
                            BaseMatch.Enum("Animation_Mode","block_by_block","layer_by_layer").add_leaves(
                                BaseMatch.Float("Animation_Seconds").add_leaves(
                                    Command_Structure,
                                    BaseMatch.END_NODE
                                ),
                                BaseMatch.END_NODE
                            ),
                            Command_Structure,
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            )
        ),
        BaseMatch.Char("Model","delete").add_leaves(
            *SpecialMatch.String_Tree("Structure_Name", BaseMatch.END_NODE )
        )
)




def Generate_Parser_Tree(Need_Trans:tuple, Start_Version:int, End_Version:int) :
    Command_Start = BaseMatch.KeyWord("Command_Start","/")
    if End_Version >= 1 and Need_Trans[1] : Command_Start.add_leaves(Setblock, Testforblock, Clone, Fill)
    if End_Version >= 1 and Need_Trans[2] : Command_Start.add_leaves(Summon)
    if End_Version >= 1 and Need_Trans[3] : Command_Start.add_leaves(Structure)

    if Start_Version == 0 : Old_Execute(Command_Start)
    elif Start_Version == 1 : NewExecute(Command_Start)

    Command_Tree1 = SpecialMatch.Command_Root().add_leaves( Command_Start )
    Command_Tree1.add_leaves(*Command_Tree1.tree_leaves[0].tree_leaves)

    return ParserSystem.Command_Parser(Command_Tree1)











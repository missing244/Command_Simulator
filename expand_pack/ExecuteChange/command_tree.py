from main_source.bedrock_edition.command_class.parser import SpecialMatch,BaseMatch

Command_Tree = SpecialMatch.Command_Root().add_leaves( 
    BaseMatch.KeyWord("Command_Start","/").add_leaves(
        BaseMatch.Char("Command","setblock").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.AnyString("Block_ID").add_leaves(
                    SpecialMatch.BE_BlockState_Tree( 
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
        ),
        BaseMatch.Char("Command","testforblock").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.AnyString("Block_ID").add_leaves(
                    SpecialMatch.BE_BlockState_Tree( BaseMatch.END_NODE ),
                    BaseMatch.Int("Block_Data").add_leaves( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )    
        ),
        BaseMatch.Char("Command","clone").add_leaves(
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
                                    SpecialMatch.BE_BlockState_Tree( BaseMatch.END_NODE ),
                                    BaseMatch.Int("Block_Data").add_leaves( BaseMatch.END_NODE )
                                )
                            )
                        ),
                        BaseMatch.END_NODE
                    )
                )
            )    
        ),
        BaseMatch.Char("Command","fill").add_leaves(
            *SpecialMatch.Pos_Tree(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.AnyString("Block_ID").add_leaves(
                        SpecialMatch.BE_BlockState_Tree( 
                            BaseMatch.Char("Fill_Mode","replace").add_leaves(
                                BaseMatch.AnyString("Block_ID").add_leaves(
                                    SpecialMatch.BE_BlockState_Tree( BaseMatch.END_NODE ),
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
        ),
        BaseMatch.Char("Command","execute").set_version(1,19,50,"max"),
        BaseMatch.Char("Command","execute").set_version(1,19,50,"min"),
        BaseMatch.AnyMsg("Any_Command").add_leaves( BaseMatch.END_NODE )
    )
)
Command_Tree.add_leaves(*Command_Tree.tree_leaves[0].tree_leaves)

Command_Tree.tree_leaves[-3].add_leaves(
    *SpecialMatch.BE_Selector_Tree(
        *SpecialMatch.Pos_Tree(
            BaseMatch.Char("Block_Test","detect").add_leaves(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.AnyString("Block_ID").add_leaves(
                        BaseMatch.Int("Block_Data").add_leaves( *Command_Tree.tree_leaves )
                    )
                )
            ),
            *Command_Tree.tree_leaves
        )
    )
)


#exexute的新语法
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
                SpecialMatch.BE_BlockState_Tree(BaseMatch.END_NODE, *Command_Execute),
                *Command_Execute,
                BaseMatch.END_NODE
            ),
            BaseMatch.AnyString("Block_ID").set_version(1,19,70,"max").add_leaves(
                BaseMatch.Int("Block_Data").add_leaves(BaseMatch.END_NODE, *Command_Execute),
                SpecialMatch.BE_BlockState_Tree(*Command_Execute),
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
Command_Tree.tree_leaves[-2].add_leaves(*Command_Execute)
















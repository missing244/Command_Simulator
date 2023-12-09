from . import BaseMatch,SpecialMatch,JsonPaser

#1.16.0的replaceitem没有destroy和keep模式，这里是Old_Item_Handling后面的
Command_Replaceitem = BaseMatch.AnyString("Item_Type").add_leaves(
        BaseMatch.Int("Amount").add_leaves(
            BaseMatch.Int("Data").add_leaves(
                JsonPaser.Json_Tree( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.END_NODE
    )

#structure的load可选动画以后
Command_Structure = BaseMatch.Enum("Include_Entities","true","false").add_leaves(
    BaseMatch.Enum("Include_Blocks","true","false").add_leaves(
        BaseMatch.Enum("Waterlogged","true","false").add_leaves(
            BaseMatch.Float("Integrity").add_leaves(
                BaseMatch.AnyString("Seed").add_leaves( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.END_NODE
    ),
    BaseMatch.END_NODE
)

#summon末尾的Event和Name
Command_Summon = BaseMatch.AnyString("Event_Type").add_leaves(
    BaseMatch.AnyString("Name").add_leaves( BaseMatch.END_NODE ),
    BaseMatch.END_NODE
)

#teleport和tp的Check_For_Blocks部分
Command_Teleport_Check_For_Blocks = [
    BaseMatch.Enum("Check_For_Blocks","true","false").add_leaves( BaseMatch.END_NODE ),
    BaseMatch.END_NODE
]

#teleport和tp的facing部分
Command_Teleport_Rotation = SpecialMatch.Pos_Tree(
    *SpecialMatch.Rotation_Tree(
        *Command_Teleport_Check_For_Blocks
    ),
    BaseMatch.Char("Argument","facing").add_leaves(
        *SpecialMatch.Pos_Tree(
            *Command_Teleport_Check_For_Blocks
        ),
        *SpecialMatch.BE_Selector_Tree(
            *Command_Teleport_Check_For_Blocks
        )
    ),
    BaseMatch.END_NODE
)

#teleport和tp的整合
Command_Teleport = [
    *SpecialMatch.BE_Selector_Tree(
        *SpecialMatch.BE_Selector_Tree(
            *Command_Teleport_Check_For_Blocks
        ),
        *SpecialMatch.Pos_Tree(
            *Command_Teleport_Check_For_Blocks
        ),
        *Command_Teleport_Rotation,
        *Command_Teleport_Check_For_Blocks
    ),
    *SpecialMatch.Pos_Tree(
        *Command_Teleport_Check_For_Blocks
    ),
    *Command_Teleport_Rotation
]

#title和titleraw的非JSON部分
Command_Title = SpecialMatch.BE_Selector_Tree(
    BaseMatch.Enum("Model","clear","reset").add_leaves(
        BaseMatch.END_NODE
    ),
    BaseMatch.Char("Model","times").add_leaves(
        BaseMatch.Int("Fade_In").add_leaves(
            BaseMatch.Int("Fade_Out").add_leaves(
                BaseMatch.Int("Fade_Out").add_leaves(
                )
            )
        )
    )
)

#后面打✓的是完整测试过的
#加V的是检查过版本的

Command_Tree = SpecialMatch.Command_Root().add_leaves(
    # ability ✓ V
    BaseMatch.Char("Command","ability").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Enum("Argument","worldbuilder","mayfly","mute").add_leaves(
                BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        )
    ),
    # alwaysday ✓ V
    BaseMatch.Char("Command","alwaysday").add_leaves( 
        BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE ) ,
        BaseMatch.END_NODE
    ),
    # camera ✓ V ps: 1.20.10.23加入了facing,不过在1.20.20.22以前属于实验玩法
    BaseMatch.Char("Command","camera").set_version(1,20,30,"min").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Char("Argument","clear").add_leaves( 
                BaseMatch.END_NODE 
            ),
            BaseMatch.Char("Argument","fade").add_leaves( 
                BaseMatch.Char("Color","color").add_leaves( 
                    BaseMatch.Int("Color_Red").add_leaves( 
                        BaseMatch.Int("Color_Green").add_leaves( 
                            BaseMatch.Int("Color_Blue").add_leaves( BaseMatch.END_NODE )
                        )
                    )
                ),
                BaseMatch.Char("Time","time").add_leaves(
                    BaseMatch.Float("Fade_In").add_leaves(
                        BaseMatch.Float("Hold").add_leaves(
                            BaseMatch.Float("Fade_Out").add_leaves(
                                BaseMatch.Char("Color","color").add_leaves(
                                    BaseMatch.Int("Color_Red").add_leaves( 
                                        BaseMatch.Int("Color_Green").add_leaves( 
                                            BaseMatch.Int("Color_Blue").add_leaves( BaseMatch.END_NODE )
                                        )
                                    )
                                ),
                                BaseMatch.END_NODE
                            )
                        )
                    )
                ),
                BaseMatch.END_NODE
            ),
            BaseMatch.Char("Argument","set").add_leaves(
                BaseMatch.AnyString("Camera_Type").add_leaves(
                    BaseMatch.END_NODE,
                    BaseMatch.Char("Type_Argument","default").add_leaves( BaseMatch.END_NODE ),
                    BaseMatch.Char("Type_Argument","ease").add_leaves(
                        BaseMatch.Float("Camera_Ease_Time").add_leaves(
                            BaseMatch.AnyString("Camera_Type").add_leaves(
                                BaseMatch.END_NODE,
                                BaseMatch.Char("Camera_Type_Argument","default").add_leaves( BaseMatch.END_NODE ),
                                BaseMatch.Char("Camera_Type_Argument","facing").add_leaves(
                                    *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
                                    *SpecialMatch.Pos_Tree( BaseMatch.END_NODE )
                                ),
                                BaseMatch.Char("Camera_Type_Argument","pos").add_leaves(
                                    *SpecialMatch.Pos_Tree( 
                                        BaseMatch.END_NODE,
                                        BaseMatch.Char("Camera_Type_Argument","facing").add_leaves(
                                            *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
                                            *SpecialMatch.Pos_Tree( BaseMatch.END_NODE )
                                        ),
                                        BaseMatch.Char("Camera_Type_Argument","rot").add_leaves(
                                            *SpecialMatch.Rotation_Tree( BaseMatch.END_NODE )
                                        ),
                                    )
                                ),
                                BaseMatch.Char("Camera_Type_Argument","rot").add_leaves(
                                    *SpecialMatch.Rotation_Tree( BaseMatch.END_NODE )
                                )
                            )
                        )
                    ),
                    BaseMatch.Char("Type_Argument","facing").add_leaves(
                        *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
                        *SpecialMatch.Pos_Tree( BaseMatch.END_NODE )
                    ),
                    BaseMatch.Char("Type_Argument","pos").add_leaves(
                        *SpecialMatch.Pos_Tree( 
                            BaseMatch.END_NODE,
                            BaseMatch.Char("Camera_Type_Argument","facing").add_leaves(
                                *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
                                *SpecialMatch.Pos_Tree( BaseMatch.END_NODE )
                            ),
                            BaseMatch.Char("Camera_Type_Argument","rot").add_leaves(
                                *SpecialMatch.Rotation_Tree( BaseMatch.END_NODE )
                            ),
                        )    
                    ),
                    BaseMatch.Char("Type_Argument","rot").add_leaves(
                        *SpecialMatch.Rotation_Tree( BaseMatch.END_NODE )
                    )
                )
            )
        )
    ),
    # camerashake ✓ V
    BaseMatch.Char("Command","camerashake").add_leaves( 
        BaseMatch.Char("Argument","add").add_leaves( 
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.Float("Intensity").add_leaves(
                    BaseMatch.Float("Time").add_leaves(
                        BaseMatch.Enum("Camerashake_Type","positional","rotational").set_version(1,16,10,"min").add_leaves(BaseMatch.END_NODE),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ), 
                BaseMatch.END_NODE
            )
        ),
        BaseMatch.Char("Argument","stop").set_version(1,16,21,"min").add_leaves( 
            *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE )
        )
    ),
    # clear ✓ V
    BaseMatch.Char("Command","clear").add_leaves( 
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyString("Item_ID").add_leaves(
                BaseMatch.Int("Data").add_leaves(
                    BaseMatch.Int("Max_Count").add_leaves(BaseMatch.END_NODE),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            ), 
            BaseMatch.END_NODE
        ),
        BaseMatch.END_NODE
    ),
    # clearspawnpoint ✓ V
    BaseMatch.Char("Command","clearspawnpoint").set_version(1,16,10,"min").add_leaves( 
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.END_NODE
        ),
        BaseMatch.END_NODE
    ),
    # say
    BaseMatch.Char("Command","say").add_leaves( 
        BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE )
    ),
    # daylock ✓ V
    BaseMatch.Char("Command","daylock").add_leaves( 
        BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE ) ,
        BaseMatch.END_NODE
    ),
    # setblock
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
    # testfor
    BaseMatch.Char("Command","testfor").add_leaves(
        *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE )
    ),
    # testforblock
    BaseMatch.Char("Command","testforblock").add_leaves(
        *SpecialMatch.Pos_Tree(
            BaseMatch.AnyString("Block_ID").add_leaves(
                SpecialMatch.BE_BlockState_Tree( BaseMatch.END_NODE ),
                BaseMatch.Int("Block_Data").add_leaves( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            )
        )    
    ),
    # testforblocks
    BaseMatch.Char("Command","testforblocks").add_leaves(
        *SpecialMatch.Pos_Tree(
            *SpecialMatch.Pos_Tree(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.Enum("Model","masked","all").add_leaves( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )
        )
    ),
    # clone ✓ V
    BaseMatch.Char("Command","clone").add_leaves(
        *SpecialMatch.Pos_Tree(
            *SpecialMatch.Pos_Tree(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.Enum("Mask_Mode","replace","masked").add_leaves(
                        BaseMatch.Enum("Clone_Mode","force","move","normal").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.Enum("Mask_Mode","filtered").add_leaves(
                        BaseMatch.Enum("Clone_Mode","force","move","normal").add_leaves(
                            BaseMatch.AnyString("Block_ID").add_leaves(
                                SpecialMatch.BE_BlockState_Tree( BaseMatch.END_NODE ),
                                BaseMatch.Int("Block_Data").set_version(1,19,70,"max").add_leaves( BaseMatch.END_NODE )
                            )
                        )
                    ),
                    BaseMatch.END_NODE
                )
            )
        )    
    ),
    # damage
    BaseMatch.Char("Command","damage").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Int("Amount").add_leaves(
                BaseMatch.AnyString("Damager_Type").add_leaves(
                    BaseMatch.Char("Value","entity").add_leaves(
                        *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE )
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            )
        )
    ),
    # deop
    BaseMatch.Char("Command","deop").add_leaves(
        *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE )
    ),
    # op
    BaseMatch.Char("Command","op").add_leaves(
        *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE )
    ),
    # dialogue  NPC相关
    BaseMatch.Char("Command","dialogue").add_leaves(
        BaseMatch.Char("Argument","open").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                *SpecialMatch.BE_Selector_Tree(
                    BaseMatch.AnyString("Scene_Name").add_leaves( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )
        ),
        BaseMatch.Char("Argument","change").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.AnyString("Scene_Name").add_leaves(
                    *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )
        )
    ),
    # difficulty
    BaseMatch.Char("Command","difficulty").add_leaves(
        BaseMatch.Enum("Difficulty","peaceful","easy","normal","hard","p","e","n","h").add_leaves( BaseMatch.END_NODE ),
        BaseMatch.Int("Difficulty").add_leaves( BaseMatch.END_NODE )
    ),
    # effect
    BaseMatch.Char("Command","effect").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Char("Argument","clear").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.AnyString("Effect_Type").add_leaves(
                BaseMatch.Int("Seconds").add_leaves(
                    BaseMatch.Int("Amplifier").add_leaves(
                        BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            )
        )
    ),
    # enchant 附魔
    BaseMatch.Char("Command","enchant").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyString("Effect_Type").add_leaves(
                BaseMatch.Int("Level").add_leaves( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            ),
            BaseMatch.Int("Enchantment_ID").add_leaves(
                BaseMatch.Int("Level").add_leaves( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            )
        )
    ),
    # event
    BaseMatch.Char("Command","event").add_leaves(
        BaseMatch.Char("Argument","entity").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.AnyString("Event_ID").add_leaves( BaseMatch.END_NODE )
            )
        )
    ),
    # fill
    BaseMatch.Char("Command","fill").add_leaves(
        *SpecialMatch.Pos_Tree(
            *SpecialMatch.Pos_Tree(
                BaseMatch.AnyString("Block_ID").add_leaves(
                    SpecialMatch.BE_BlockState_Tree(
                        BaseMatch.Char("Fill_Mode","replace").add_leaves(
                            BaseMatch.AnyString("Block_ID").add_leaves(
                                SpecialMatch.BE_BlockState_Tree( BaseMatch.END_NODE )
                            ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.Enum("Fill_Mode","hollow","keep","outline","replace").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.Int("Block_Data").add_leaves( 
                        BaseMatch.Char("Fill_Mode","replace").add_leaves(
                            BaseMatch.AnyString("Block_ID").add_leaves(
                                BaseMatch.Int("Block_Data").add_leaves(BaseMatch.END_NODE)
                            ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.Enum("Fill_Mode","hollow","keep","outline","replace").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            )
        )    
    ),
    # tellraw
    BaseMatch.Char("Command","tellraw").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            JsonPaser.Json_Tree( BaseMatch.END_NODE )
        )
    ),
    # fog
    BaseMatch.Char("Command","fog").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Char("Mode_Delete","push").add_leaves(
                BaseMatch.AnyString("Fog_Type").add_leaves(
                    BaseMatch.AnyString("User_Provided_Id").add_leaves( BaseMatch.END_NODE )
                )
            ),
            BaseMatch.Enum("Mode_Delete","pop","remove").add_leaves(
                BaseMatch.AnyString("User_Provided_Id").add_leaves( BaseMatch.END_NODE )
            )
        )
    ),
    # function
    BaseMatch.Char("Command","function").add_leaves(
        BaseMatch.AnyString("Name_Filepath",terminator=" ").add_leaves( BaseMatch.END_NODE )
    ),
    # gamemode
    BaseMatch.Char("Command","gamemode").add_leaves(
        BaseMatch.Enum("Game_Mode","survival","creative","adventure","default","spectator").add_leaves(
            *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        ),
        BaseMatch.Int("Game_Mode").add_leaves(
            *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        )
    ),
    # gamerule
    BaseMatch.Char("Command","gamerule").add_leaves(
        BaseMatch.AnyString("Gamerule_Type").add_leaves(
            BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.Int("Gamerule_Value").add_leaves( BaseMatch.END_NODE )
        )
    ),
    # give
    BaseMatch.Char("Command","give").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyString("Item_Type").add_leaves(
                BaseMatch.Int("Amount_Int").add_leaves(
                    BaseMatch.Int("Data_Int").add_leaves(
                        JsonPaser.Json_Tree( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            )
        )
    ),
    # inputpermission 摄像机和移动权限控制
    BaseMatch.Char("Command","inputpermission").add_leaves(
        BaseMatch.Char("Argument","query").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.Enum("Permission","camera","movement").add_leaves(
                    BaseMatch.Enum("State","enabled","disabled").add_leaves( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )
        ),
        BaseMatch.Char("Argument","set").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.Enum("Permission","camera","movement").add_leaves(
                    BaseMatch.Enum("State","enabled","disabled").add_leaves( BaseMatch.END_NODE )
                )
            )
        )
    ),
    # kick
    BaseMatch.Char("Command","kick").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        )
    ),
    # kill
    BaseMatch.Char("Command","kill").add_leaves(
        *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE ),
        BaseMatch.END_NODE
    ),
    BaseMatch.Char("Command","list").add_leaves( BaseMatch.END_NODE ),
    BaseMatch.Char("Command","locate").set_version(1,19,10,"min").add_leaves(
        BaseMatch.Char("Argument","biome").add_leaves(
            BaseMatch.AnyString("Biome_Type").add_leaves( BaseMatch.END_NODE )
        ),
        BaseMatch.Char("Argument","structure").add_leaves(
            BaseMatch.AnyString("Structure_Type").add_leaves(
                BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            )
        )
    ),
    # locate
    BaseMatch.Char("Command","locate").set_version(1,19,10,"max").add_leaves(
        BaseMatch.AnyString("Structure_Type").add_leaves( BaseMatch.END_NODE )
    ),
    # loot
    BaseMatch.Char("Command","loot").add_leaves(
        BaseMatch.Char("Argument","give").set_version(1,18,30,"min").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.Char("Argument","kill").add_leaves(
                    *SpecialMatch.BE_Selector_Tree(
                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                ),
                BaseMatch.Char("Argument","loot").add_leaves(
                    BaseMatch.AnyString("Loot_Table").add_leaves(
                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                )
            )
        ),
        BaseMatch.Char("Argument","insert").set_version(1,18,30,"min").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.Char("Argument","kill").add_leaves(
                    *SpecialMatch.BE_Selector_Tree(
                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                ),
                BaseMatch.Char("Argument","loot").add_leaves(
                    BaseMatch.AnyString("Loot_Table").add_leaves(
                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                )
            )
        ),
        BaseMatch.Char("Argument","spawn").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.Char("Argument","kill").add_leaves(
                    *SpecialMatch.BE_Selector_Tree(
                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                ),
                BaseMatch.Char("Argument","loot").add_leaves(
                    BaseMatch.AnyString("Loot_Table").add_leaves(
                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                )
            )
        ),
        BaseMatch.Char("Argument","replace").add_leaves(
            BaseMatch.Char("Argument","block").set_version(1,19,40,"min").add_leaves(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.Char("Slot","slot.container").add_leaves(
                        BaseMatch.Int("Slot_Id").add_leaves(
                            BaseMatch.Int("Count").add_leaves(
                                BaseMatch.Char("Argument","kill").add_leaves(
                                    *SpecialMatch.BE_Selector_Tree(
                                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                        BaseMatch.END_NODE
                                    )
                                ),
                                BaseMatch.Char("Argument","loot").add_leaves(
                                    BaseMatch.AnyString("Loot_Table").add_leaves(
                                        BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                        BaseMatch.END_NODE
                                    )
                                )
                            ),
                            BaseMatch.Char("Argument","kill").add_leaves(
                                *SpecialMatch.BE_Selector_Tree(
                                    BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                    BaseMatch.END_NODE
                                )
                            ),
                            BaseMatch.Char("Argument","loot").add_leaves(
                                BaseMatch.AnyString("Loot_Table").add_leaves(
                                    BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                    BaseMatch.END_NODE
                                )
                            )
                        )
                    )
                )
            ),
            BaseMatch.Char("Argument","entity").set_version(1,19,00,"min").add_leaves(
                *SpecialMatch.BE_Selector_Tree(
                    BaseMatch.AnyString("Slot_Type").add_leaves(
                        BaseMatch.Int("Slot_ID").add_leaves(
                            BaseMatch.Char("Argument","kill").add_leaves(
                                *SpecialMatch.BE_Selector_Tree(
                                    BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                    BaseMatch.END_NODE
                                )
                            ),
                            BaseMatch.Char("Argument","loot").add_leaves(
                                BaseMatch.AnyString("Loot_Table").add_leaves(
                                    BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                    BaseMatch.END_NODE
                                )
                            )
                        ),
                        BaseMatch.Char("Argument","kill").add_leaves(
                            *SpecialMatch.BE_Selector_Tree(
                                BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                BaseMatch.END_NODE
                            )
                        ),
                        BaseMatch.Char("Argument","loot").add_leaves(
                            BaseMatch.AnyString("Loot_Table").add_leaves(
                                BaseMatch.AnyString("Tool_Type").add_leaves( BaseMatch.END_NODE ),
                                BaseMatch.END_NODE
                            )
                        )
                    )
                )
            )
        )
    ),
    # me
    BaseMatch.Char("Command","me").add_leaves(
        BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE )
    ),
    # mobevent 生物事件
    BaseMatch.Char("Command","mobevent").add_leaves(
        BaseMatch.AnyString("Event_ID").add_leaves(
            BaseMatch.Enum("Value","true","false").add_leaves( BaseMatch.END_NODE )
        ),
        BaseMatch.END_NODE
    ),
    # tell
    BaseMatch.Char("Command","tell").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE )
        )
    ),
    # msg
    BaseMatch.Char("Command","msg").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE )
        )
    ),
    # w
    BaseMatch.Char("Command","w").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE )
        )
    ),
    # music
    BaseMatch.Char("Command","music").add_leaves(
        BaseMatch.Enum("Argument","play","queue").add_leaves(
            BaseMatch.AnyString("Track_Name").add_leaves(
                BaseMatch.Float("Volume").add_leaves(
                    BaseMatch.Float("Fade_Seconds").add_leaves(
                        BaseMatch.Enum("Repeat_Mode","play_once","loop").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            )
        ),
        BaseMatch.Char("Argument","stop").add_leaves(
            BaseMatch.Float("Fade_Seconds").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        ),
        BaseMatch.Char("Command","volume").add_leaves(
            BaseMatch.Float("Volume").add_leaves( BaseMatch.END_NODE )
        )
    ),
    # particle
    BaseMatch.Char("Command","particle").add_leaves(
        BaseMatch.AnyString("Particle_Type").add_leaves(
            *SpecialMatch.Pos_Tree( BaseMatch.END_NODE )
        ),
        BaseMatch.END_NODE
    ),
    # permission 和 ops 一样 服务器控制台重新加载权限命令
    BaseMatch.Char("Command","permission").add_leaves(
        BaseMatch.Enum("Argument","list","reload").add_leaves( BaseMatch.END_NODE )
    ),
    #ops
    BaseMatch.Char("Command","ops").add_leaves(
        BaseMatch.Enum("Argument","list","reload").add_leaves( BaseMatch.END_NODE )
    ),
    # playanimation
    BaseMatch.Char("Command","playanimation").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyString("animation_Type").add_leaves(
                BaseMatch.AnyString("Next_State_Type").add_leaves(
                    BaseMatch.Float("Blend_Out_Time").add_leaves(
                        BaseMatch.AnyString("Stop_Expression_Type").add_leaves(
                            BaseMatch.AnyString("Controller_Type").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            )
        )
    ),
    # playsound
    BaseMatch.Char("Command","playsound").add_leaves(
        BaseMatch.AnyString("Sound_Type").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.Float("Volume").add_leaves(
                        BaseMatch.Float("Pitch").add_leaves(
                            BaseMatch.Float("Minimum_Volume").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        )
    ),
    # recipe
    BaseMatch.Char("Command","recipe").add_leaves(
        BaseMatch.Enum("Argument","give","take").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.AnyString("Recipe_Type").add_leaves( BaseMatch.END_NODE )
            )
        )
    ),
    # replaceitem
    BaseMatch.Char("Command","replaceitem").add_leaves(
        BaseMatch.Char("Argument","block").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.Char("Slot_Type","slot.container").add_leaves(
                    BaseMatch.Int("Slot_Id").add_leaves(
                    BaseMatch.Enum("Old_Item_Handling","keep","destroy").set_version(1,16,0,"min").add_leaves( Command_Replaceitem ),
                    Command_Replaceitem
                    )
                )
            )
        ),
        BaseMatch.Char("Argument","entity").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.AnyString("Slot_Type").add_leaves(
                    BaseMatch.Int("Slot_Id").add_leaves(
                    BaseMatch.Enum("Old_Item_Handling","keep","destroy").set_version(1,16,0,"min").add_leaves( Command_Replaceitem ),
                    Command_Replaceitem
                    )
                )
            )
        )
    ),
    # ride
    BaseMatch.Char("Command","ride").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Char("Argument","start_riding").add_leaves(
                *SpecialMatch.BE_Selector_Tree(
                    BaseMatch.Enum("Teleport_Rules","teleport_ride","teleport_rider").add_leaves(
                        BaseMatch.Enum("How_To_Fill","if_group_fits","until_full").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            ),
            BaseMatch.Enum("Argument","evict_riders","stop_riding").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.Char("Command","summon_ride").add_leaves(
                *SpecialMatch.BE_Selector_Tree(
                    BaseMatch.AnyString("Event_Type").add_leaves(
                        BaseMatch.AnyString("Name_Type").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            ),
            BaseMatch.Char("Command","summon_rider").add_leaves(
                *SpecialMatch.BE_Selector_Tree(
                    BaseMatch.Enum("Ride_Rules","no_ride_change","reassign_rides","skip_riders").add_leaves(
                        BaseMatch.AnyString("Event_Type").add_leaves(
                            BaseMatch.AnyString("Name_Type").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            )
        )
    ),
    # schedule
    BaseMatch.Char("Command","schedule").add_leaves(
        BaseMatch.Char("Argument","on_area_loaded").add_leaves(
            BaseMatch.Char("Argument","add").add_leaves(
                *SpecialMatch.Pos_Tree(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.AnyString("Function").add_leaves( BaseMatch.END_NODE )
                    )
                ),
                BaseMatch.Char("Argument","circle").add_leaves(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.Int("Radius").add_leaves(
                            BaseMatch.AnyString("Function").add_leaves( BaseMatch.END_NODE )
                        )
                    )
                ),
                BaseMatch.Char("Argument","tickingarea").add_leaves(
                    BaseMatch.AnyString("Name").add_leaves(
                        BaseMatch.AnyString("Function").add_leaves( BaseMatch.END_NODE )
                    )
                )
            )
        )
    ),
    # scoreboard
    BaseMatch.Char("Command","scoreboard").add_leaves(
        BaseMatch.Char("Argument","objectives").add_leaves(
            BaseMatch.Char("Argument","add").add_leaves(
                *SpecialMatch.Scoreboard_Objective_Tree(
                    BaseMatch.Char("Argument","dummy").add_leaves(
                        *SpecialMatch.Scoreboard_Objective_Tree( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    )
                )
            ),
            BaseMatch.Char("Argument","list").add_leaves(
                BaseMatch.END_NODE
            ),
            BaseMatch.Char("Argument","remove").add_leaves(
                *SpecialMatch.Scoreboard_Objective_Tree( BaseMatch.END_NODE )
            ),
            BaseMatch.Char("Argument","setdisplay").add_leaves(
                BaseMatch.Enum("Show_Type","list","sidebar").add_leaves(
                    *SpecialMatch.Scoreboard_Objective_Tree(
                        BaseMatch.Enum("Sort","ascending","descending").add_leaves( BaseMatch.END_NODE ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                ),
                BaseMatch.Char("Show_Type","command").add_leaves(
                    *SpecialMatch.Scoreboard_Objective_Tree( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            )
        ),
        BaseMatch.Char("Argument","objectives").add_leaves(
            BaseMatch.Enum("Argument","set","add","remove").add_leaves(
                *SpecialMatch.Scoreboard_Entity_Name_Tree(
                    *SpecialMatch.Scoreboard_Objective_Tree(
                        BaseMatch.Int("Count").add_leaves( BaseMatch.END_NODE )
                    )
                )
            ),
            BaseMatch.Char("Argument","list").add_leaves(
                *SpecialMatch.Scoreboard_Entity_Name_Tree( BaseMatch.END_NODE ),
                BaseMatch.END_NODE 
            ),
            BaseMatch.Char("Argument","operation").add_leaves(
                *SpecialMatch.Scoreboard_Entity_Name_Tree(
                    *SpecialMatch.Scoreboard_Objective_Tree(
                        BaseMatch.Enum("Operate","+=","-=","*=","/=","%=","=","<",">","><").add_leaves(
                            *SpecialMatch.Scoreboard_Entity_Name_Tree(
                                *SpecialMatch.Scoreboard_Objective_Tree( BaseMatch.END_NODE )
                            )
                        )
                    )
                )
            ),
            BaseMatch.Char("Argument","random").add_leaves(
                *SpecialMatch.Scoreboard_Entity_Name_Tree(
                    *SpecialMatch.Scoreboard_Objective_Tree(
                        BaseMatch.Int("min").add_leaves(
                            BaseMatch.Int("max").add_leaves( BaseMatch.END_NODE )
                        )
                    )
                )
            ),
            BaseMatch.Char("Argument","reset").add_leaves(
                *SpecialMatch.Scoreboard_Entity_Name_Tree(
                    *SpecialMatch.Scoreboard_Objective_Tree( BaseMatch.END_NODE ),
                    BaseMatch.END_NODE
                )
            ),
            BaseMatch.Char("Argument","test").add_leaves(
                *SpecialMatch.Scoreboard_Entity_Name_Tree(
                    *SpecialMatch.Scoreboard_Objective_Tree(
                        BaseMatch.Int("min").add_leaves(
                            BaseMatch.Int("max").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.KeyWord("max","*").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.KeyWord("min","*").add_leaves(
                            BaseMatch.Int("max").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.KeyWord("max","*").add_leaves( BaseMatch.END_NODE ),
                            BaseMatch.END_NODE
                        )
                    )
                )
            )
        )
    ),
    BaseMatch.Char("Command","setmaxplayers").add_leaves(
        BaseMatch.Int("Max_Players").add_leaves( BaseMatch.END_NODE )
    ),
    BaseMatch.Char("Command","setworldspawn").add_leaves(
        *SpecialMatch.Pos_Tree( BaseMatch.END_NODE ),
        BaseMatch.END_NODE
    ),
    BaseMatch.Char("Command","spawnpoint").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            *SpecialMatch.Pos_Tree( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        ),
        BaseMatch.END_NODE
    ),
    BaseMatch.Char("Command","spreadplayers").add_leaves(
        *SpecialMatch.Rotation_Tree(
            BaseMatch.Float("Spread_Distance").add_leaves(
                BaseMatch.Float("Max_Range").add_leaves(
                    *SpecialMatch.BE_Selector_Tree( BaseMatch.END_NODE )
                )
            )
        )
    ),
    BaseMatch.Char("Command","stopsound").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.AnyString("Sound_Type").add_leaves( BaseMatch.END_NODE ),
            BaseMatch.END_NODE
        )
    ),
    BaseMatch.Char("Command","structure").add_leaves(
        BaseMatch.Char("Model","save").add_leaves(
            BaseMatch.AnyString("Name").add_leaves(
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
            BaseMatch.AnyString("Name").add_leaves(
                *SpecialMatch.Pos_Tree(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.Enum("Rotation","0_degrees","90_degrees","180_degrees"",270_degrees").add_leaves(
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
            )
        ),
        BaseMatch.Char("Model","delete").add_leaves(
            BaseMatch.AnyString("Name").add_leaves( BaseMatch.END_NODE )
        )
    ),
    BaseMatch.Char("Command","summon").add_leaves(
        BaseMatch.AnyString("Entity_Type").add_leaves(
            BaseMatch.AnyString("Name").add_leaves(
                *SpecialMatch.Pos_Tree( BaseMatch.END_NODE ),
                BaseMatch.END_NODE
            )
        ),
        BaseMatch.AnyString("Entity_Type").set_version(1,19,70,"max").add_leaves(
            *SpecialMatch.Pos_Tree(
                Command_Summon,
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.AnyString("Entity_Type").set_version(1,19,70,"min").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.Float("Fade_In").add_leaves(
                    Command_Summon,
                    BaseMatch.END_NODE
                ),
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.AnyString("Entity_Type").set_version(1,19,80,"min").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.Char("Argument","facing").add_leaves(
                    *SpecialMatch.BE_Selector_Tree(
                        Command_Summon,
                        BaseMatch.END_NODE
                    ),
                    *SpecialMatch.Pos_Tree(
                        Command_Summon,
                        BaseMatch.END_NODE
                    )
                )
            ),
            BaseMatch.END_NODE
        )
    ),
    BaseMatch.Char("Command","tag").add_leaves(
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Char("Argument","add").add_leaves(
                BaseMatch.AnyString("Name").add_leaves( BaseMatch.END_NODE )
            ),
            BaseMatch.Char("Argument","remove").add_leaves(
                BaseMatch.AnyString("Name").add_leaves( BaseMatch.END_NODE )
            ),
            BaseMatch.Char("Command","list").add_leaves( BaseMatch.END_NODE )
        )
    ),
    BaseMatch.Char("Command","teleport").add_leaves(
        *Command_Teleport
    ),
    BaseMatch.Char("Command","tp").add_leaves(
        *Command_Teleport
    ),
    BaseMatch.Char("Command","tickingarea").add_leaves(
        BaseMatch.Char("Command","add").add_leaves(
            *SpecialMatch.Pos_Tree(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.AnyString("Name").add_leaves(
                        BaseMatch.Enum("Preload","true","false").add_leaves(
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    ),
                    BaseMatch.END_NODE
                )
            ),
            BaseMatch.Char("Model","circle").add_leaves(
                *SpecialMatch.Pos_Tree(
                    BaseMatch.Int("Radius").add_leaves(
                        BaseMatch.AnyString("Name").add_leaves(
                            BaseMatch.Enum("Preload","true","false").add_leaves(
                                BaseMatch.END_NODE
                            ),
                            BaseMatch.END_NODE
                        ),
                        BaseMatch.END_NODE
                    )
                )
            )
        ),
        BaseMatch.Char("Argument","remove").add_leaves(
            *SpecialMatch.Pos_Tree( BaseMatch.END_NODE ),
            BaseMatch.AnyString("Name").add_leaves( BaseMatch.END_NODE )
        ),
        BaseMatch.Char("Argument","remove_all").add_leaves(
            BaseMatch.END_NODE
        ),
        BaseMatch.Char("Argument","Preload").add_leaves(
            *SpecialMatch.Pos_Tree( BaseMatch.END_NODE ),
            BaseMatch.AnyString("Name").add_leaves( BaseMatch.END_NODE )
        ),
        BaseMatch.Char("Argument","list").add_leaves(
            BaseMatch.Char("All_Dimensions","all-dimensions").add_leaves(
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        )
    ),
    BaseMatch.Char("Command","time").add_leaves(
        BaseMatch.Char("Time_Model","add").add_leaves(
            BaseMatch.Int("Amount").add_leaves(
                BaseMatch.END_NODE
            )
        ),
        BaseMatch.Char("Time_Model","query").add_leaves(
            BaseMatch.Enum("Time_Type","daytime","gametime","day").add_leaves(
                BaseMatch.END_NODE
            )
        ),
        BaseMatch.Char("Time_Model","set").add_leaves(
            BaseMatch.Enum("Time","day","noon","sunrise","sunset","night","midnight").add_leaves(
                BaseMatch.END_NODE
            ),
            BaseMatch.Int("Time").add_leaves(
                BaseMatch.END_NODE
            )
        )
    ),
    BaseMatch.Char("Command","title").add_leaves(
        *Command_Title,
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Enum("Model","title","subtitle","actionbar").add_leaves(
                BaseMatch.AnyMsg("Msg").add_leaves( BaseMatch.END_NODE )
            )
        )
    ),
    BaseMatch.Char("Command","titleraw").add_leaves(
        *Command_Title,
        *SpecialMatch.BE_Selector_Tree(
            BaseMatch.Enum("Model","title","subtitle","actionbar").add_leaves(
                JsonPaser.Json_Tree( BaseMatch.END_NODE )
            )
        )
    ),
    BaseMatch.Char("Command","toggledownfall").add_leaves(
        BaseMatch.END_NODE
    ),
    BaseMatch.Char("Command","volumearea").add_leaves(
        BaseMatch.Char("Argument","add").add_leaves(
            BaseMatch.AnyString("Identifier").add_leaves(
                *SpecialMatch.Pos_Tree(
                    *SpecialMatch.Pos_Tree(
                        BaseMatch.AnyString("Name").add_leaves(
                            BaseMatch.END_NODE
                        )
                    )
                )
            )
        ),
        BaseMatch.Char("Argument","list").add_leaves(
            BaseMatch.Char("All_Dimensions","all-dimensions").add_leaves(
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.Char("Argument","remove").add_leaves(
            *SpecialMatch.Pos_Tree(
                BaseMatch.END_NODE
            ),
            BaseMatch.AnyString("Name").add_leaves(
                BaseMatch.END_NODE
            )
        ),
        BaseMatch.Char("Argument","remove-all").add_leaves(
            BaseMatch.END_NODE
        )
    ),
    BaseMatch.Char("Command","weather").add_leaves(
        BaseMatch.Enum("Argument","clear","rain","thunder").add_leaves(
            BaseMatch.Int("Duration").add_leaves(
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.Char("Argument","query").add_leaves(
            BaseMatch.END_NODE
        )
    ),
    BaseMatch.Char("Command","xp").add_leaves(
        BaseMatch.Int("Amount").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        ),
        BaseMatch.Int("Amount","L").add_leaves(
            *SpecialMatch.BE_Selector_Tree(
                BaseMatch.END_NODE
            ),
            BaseMatch.END_NODE
        )
    ),
    BaseMatch.Char("Command","execute").set_version(1,19,50,"max"),
    BaseMatch.Char("Command","execute").set_version(1,19,50,"min"),
)

Command_Tree.tree_leaves[-2].add_leaves(
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














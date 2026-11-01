from . import MCCommandParser as CommandParser, GameClass, CommandClass
from .. import MCStructureManage
from ..GameClass.dimension import ParticleDef, Dimension
from typing import List, Dict, Union, Literal, Tuple, Callable
import re, functools, webbrowser, json
CommonStructure = MCStructureManage.CommonStructure
MinecraftSimulator = GameClass.MinecraftSimulator
CompileError = CommandClass.CompileError
CommandContext = CommandClass.CommandContext
CommandResult = CommandClass.CommandResult
ParserResult = CommandParser.ParserResult


class TestDataSave :

    def __init__(self, main_thread:MinecraftSimulator):
        self.__main_thread = main_thread

        self.Area:CommonStructure = None
        self.Commands:List[CommandResult] = []
        self.Particles:List[ParticleDef] = []


    def set_default_area(self, dimension:Dimension, start:Tuple[int, int, int], end:Tuple[int, int, int]) :
        self.Area = self.__main_thread.StructureManage.create_structure(
            dimension, start, end)

    def set_particles(self, dimension:Dimension) :
        self.Particles.extend(dimension.Particles)




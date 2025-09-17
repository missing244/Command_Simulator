"""
## 基岩版封装数据类型
* 类**ItemType**                  : 物品对象
* 类**EntityType**                : 实体对象
* 类**ItemEntityType**            : 物品实体对象
* 类**MobType**                   : 生物对象
* 类**PlayerType**                : 玩家对象(不可实例化)
* 类**BlockPermutationType**      : 方块预设对象
* 类**BlockNbtType**              : 方块NBT对象
* 类**SubChunk**                  : 子区块(16,16,16)对象
* 类**ChunkType**                 : 区块对象
--------------------------------------------------------------------------------------------
* 常量**NoneItemNBT**             : ID为空的物品nbt对象，使用时请注意调用copy方法
--------------------------------------------------------------------------------------------
* 函数**NBTtoEntity**               : 通过NBT自动识别生成对应实体对象
* 函数**GenerateChunkLevelDBKey**   : 通过维度、坐标、操作码生成LevelDB键名
* 函数**GenerateSuperflatSubChunk** : 生成一个超平坦子区块

"""

class ModifyError(Exception) : pass
class ValueError(Exception) : pass

from .ItemType import ItemType, NoneItemNBT
from .EntityType import EntityType, ItemEntityType, MobType, PlayerType, NBTtoEntity
from .BlockType import BlockPermutationType, BlockNbtType
from .ChunkType import SubChunkType, ChunkType, GenerateChunkLevelDBKey, GenerateSuperflatSubChunk
from .OtherType import Scoreboard, Map, Structure, TickingArea



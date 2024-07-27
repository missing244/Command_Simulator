
const SingelFace_BlockDefinition = {
    //{"transmitting":false, "index": 0, "model":"same_6"}
    "minecraft:stone": {"transmitting":false, "index": 0, "model":"same_6"}
}

const DoubleFace_BlockDefinition = {}

const BlockIDTransfor = {}

const BlockStateTransfor = {}
  
export function QueryBlockRender(Block) {
    const Block_ID = Block.id

    if (Block_ID in SingelFace_BlockDefinition) return SingelFace_BlockDefinition[Block_ID]
    else if (Block_ID in DoubleFace_BlockDefinition) return DoubleFace_BlockDefinition[Block_ID]
    else throw Error(`不存在的方块ID: ${Block_ID}`)
}
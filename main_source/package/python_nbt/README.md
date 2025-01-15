# MCNBT-py - Minecraft NBT Library for Python

`MCNBT-py`是一个Python库，用于读取和编辑NBT（Named Binary Tag）数据。
NBT是Minecraft游戏中使用的一种数据存储格式，能够以二进制方式保存复杂的数据结构。
`MCNBT-py`支持标准的NBT文件处理，并提供了丰富的API来序列化和解析原始NBT数据。
它提供了读取、写入和操作NBT数据的功能，支持NBT、SNBT（String NBT）和DAT格式。

## 特点

- **多种格式支持**：支持NBT、SNBT和DAT格式的读写。支持gzip, zlib和未压缩文件
- **丰富的API**：提供丰富的API来处理各种NBT标签类型，包括复合标签（Compound）、列表（List）等。
- **异常处理**：自定义异常类，方便错误追踪和处理。
- **类型注解**：代码中包含类型注解，提高代码质量和开发体验。

[//]: # ## 安装

[//]: # ```bash
[//]: # pip install minecraft-nbt-library
[//]: # ```

##使用示例

```python
import python_nbt as nbt

# 从文件读取NBT数据
nbt_data = nbt.from_nbt_file("path/to/your/nbt/file.nbt")

# 访问NBT标签
tag = nbt_data.get_tag()
print(tag)

# 将NBT数据写入文件
nbt.write_to_nbt_file("path/to/your/output/nbt/file.nbt", nbt_data)

```

##文档


• [API文档](https://github.com/long-or/MCNBT-py/edit/main/api/main.md)：详细的API文档，包括每个类和方法的说明。

• [贡献指南](#)：如何为这个项目贡献代码。


##贡献

欢迎任何形式的贡献，包括代码、文档、测试和反馈。请查看[贡献指南](#)了解更多信息。


##许可证

这个项目在[MIT许可证](LICENSE)下发布。
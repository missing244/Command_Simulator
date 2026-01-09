# Python 的 MessagePack

[![构建状态](https://github.com/msgpack/msgpack-python/actions/workflows/wheel.yml/badge.svg)](https://github.com/msgpack/msgpack-python/actions/workflows/wheel.yml)  
[![文档状态](https://readthedocs.org/projects/msgpack-python/badge/?version=latest)](https://msgpack-python.readthedocs.io/en/latest/?badge=latest)

## 这是什么？

[MessagePack](https://msgpack.org/) 是一种高效的二进制序列化格式。  
它像 JSON 一样，可以在多种编程语言之间交换数据，但速度更快、体积更小。

本包为 Python 提供了 MessagePack 的 CPython 读写绑定。

## 安装

```bash
pip install msgpack
```

### 纯 Python 实现

msgpack 中的扩展模块（`msgpack._cmsgpack`）不支持 PyPy。  
但 msgpack 为 PyPy 提供了纯 Python 实现（`msgpack.fallback`）。

### Windows

如果无法使用二进制发行版，在 Windows 上需要安装 Visual Studio 或 Windows SDK。  
没有扩展模块时，CPython 下的纯 Python 实现性能较低。

## 使用方法

### 一次性打包与解包

```python
import msgpack

data = [1, 2, 3]
packed = msgpack.packb(data)
unpacked = msgpack.unpackb(packed)
print(unpacked)
```

### 流式解包

```python
import msgpack
from io import BytesIO

buf = BytesIO()
for i in range(3):
    buf.write(msgpack.packb(i))

buf.seek(0)
unpacker = msgpack.Unpacker(buf)
for item in unpacker:
    print(item)
```

### 自定义类型示例（datetime）

```python
import datetime
import msgpack

def encode(obj):
    if isinstance(obj, datetime.datetime):
        return {
            "__datetime__": True,
            "value": obj.strftime("%Y%m%dT%H:%M:%S")
        }
    return obj

def decode(obj):
    if "__datetime__" in obj:
        return datetime.datetime.strptime(obj["value"], "%Y%m%dT%H:%M:%S")
    return obj

data = {"time": datetime.datetime.now()}
packed = msgpack.packb(data, default=encode)
unpacked = msgpack.unpackb(packed, object_hook=decode)
```

## 安全性

- `max_buffer_size`：限制缓冲区大小，防止内存攻击  
- `strict_map_key`：限制 map 的键类型，避免哈希 DoS

## 许可证

本项目遵循 MessagePack 官方许可证。

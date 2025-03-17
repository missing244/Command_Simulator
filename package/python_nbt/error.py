"""
    error.py - 错误信息
"""


class BreakLoop(Exception): pass

class SnbtParseError(Exception): pass
class SnbtTokenError(Exception): pass

class NbtParseError(Exception): pass
class NbtFileError(Exception): pass

class NbtBufferError(Exception): pass
class NbtContextError(Exception): pass
class NbtDataError(Exception): pass

def throw_nbt_error(e, buffer, length):
    buffer.seek(buffer.tell() - length)
    value = buffer.read(length)
    if len(value) >= 10:
        value = value[0:4] + b'...' + value[-3:]
    raise NbtParseError("%s (%s) 位于 %s 到 %s字节" % (e.args[0], value, buffer.tell() - length, buffer.tell()))

def buffer_read(buffer, length, msg):
    byte = buffer.read(length)
    if len(byte) != length: raise NbtParseError("ELO Error，期望%s字节，实际为%s字节（%s）" % (length, len(byte), msg))
    return byte

# `mccmdhl2` - Minecraft Bedrock command parser and autocompleter.
# Copyright (C) 2023  CBerJun<cberjun@163.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Implement some of the `contextlib` features *INCOMPLETELY*
for performance reason.
PLEASE USE THIS CAREFULLY, ESPECIALLY WHEN DEALING WITH EXCEPTIONS.
"""

__all__ = ["contextmanager", "ExitStack"]

class _GeneratorContextManager:
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        return next(self.gen)

    def __exit__(self, *exc_info):
        if exc_info[0] is not None:
            raise
        try:
            next(self.gen)
        except StopIteration:
            pass
        else:
            raise RuntimeError("generator didn't stop")

def contextmanager(func):
    """Used as a decorator to turn a generator into a context manager.
    NOTE This implementation will bypass the exceptions and will
    re-raise immediately without going back to generator.
    """
    def _decorated(*args, **kwds):
        return _GeneratorContextManager(func(*args, **kwds))
    return _decorated

class ExitStack:
    """*Similar* to `contextlib.ExitStack` but is faster.
    NOTE Use this carefully since we use a special way to handle
    exceptions.
    """
    def __init__(self):
        self.exits = []

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if exc_info[0] is not None:
            raise
        for cm, exit in self.exits:
            exit(cm, None, None, None)

    def enter_context(self, cm):
        # `cm` is supposed to be `ContextManager`
        res = cm.__enter__()
        self.exits.insert(0, (cm, type(cm).__exit__))
        return res

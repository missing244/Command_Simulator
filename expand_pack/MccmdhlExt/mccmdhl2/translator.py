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

"""Localization of error messages and auto-completing hints."""

from typing import List, Optional
import json

__all__ = ["Translator"]

class Translator:
    def __init__(self, parent: Optional["Translator"] = None):
        self.map = {}
        if parent:
            self.map.update(parent.map)

    @classmethod
    def from_json(cls, path: str, **kwds):
        inst = cls()
        with open(path, "r", **kwds) as file:
            j = json.load(file)
        def _handle(obj: dict, _prefix: List[str] = []):
            assert isinstance(obj, dict)
            for key, value in obj.items():
                p = _prefix.copy()
                p.append(key)
                if isinstance(value, dict):
                    _handle(value, p)
                elif isinstance(value, str):
                    inst.map[".".join(p)] = value
                else:
                    raise ValueError("Wrong message translation file format")
        _handle(j)
        return inst

    @classmethod
    def empty_translation(cls):
        return cls()

    @classmethod
    def merge_from(cls, *translators: "Translator"):
        res = {}
        for trans in translators:
            res.update(trans.map)
        inst = cls()
        inst.map = res
        return inst

    def get(self, key: str):
        return self.map.get(key, key)

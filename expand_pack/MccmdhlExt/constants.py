import os
import tkinter
import mccmdhl2

__all__ = ["ALL_WRAPS", "ALL_VERSIONS",
           "BG_UNPRESSED", "BG_PRESSED", "BUTTON_FONT",
           "DIR"]

# Get all MC versions
_all_versions = set()
def _version_decorator(func):
    def _wrapped(version):
        _all_versions.add(version)
        return func(version)
    return _wrapped
mccmdhl2.nodes.VersionGe = _version_decorator(mccmdhl2.nodes.VersionGe)
mccmdhl2.nodes.VersionLt = _version_decorator(mccmdhl2.nodes.VersionLt)
mccmdhl2.get_default_tree()
ALL_VERSIONS = sorted(_all_versions, reverse=True)

# UI constants
ALL_WRAPS = (tkinter.NONE, tkinter.WORD, tkinter.CHAR)
BG_UNPRESSED = "#00ff7f"
BG_PRESSED = "#ff4500"
BUTTON_FONT = {
    "background": BG_UNPRESSED,
    "font": ("Arial", 9),
}

# Path
DIR = os.path.realpath(os.path.join(__file__, os.pardir))

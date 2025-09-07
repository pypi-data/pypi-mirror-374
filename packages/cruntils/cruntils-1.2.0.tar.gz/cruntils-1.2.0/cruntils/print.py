
"""
Colour printing in vanilla Python.
"""

from enum import Enum

class _EAnsiColours(Enum):
    FGBLACK   = "30"
    FGRED     = "31"
    FGGREEN   = "32"
    FGYELLOW  = "33"
    FGBLUE    = "34"
    FGMAGENTA = "35"
    FGCYAN    = "36"
    FGWHITE   = "37"

    BGBLACK   = "40"
    BGRED     = "41"
    BGGREEN   = "42"
    BGYELLOW  = "43"
    BGBLUE    = "44"
    BGMAGENTA = "45"
    BGCYAN    = "46"
    BGWHITE   = "47"

    FGBRIGHTBLACK   = "90"
    FGBRIGHTRED     = "91"
    FGBRIGHTGREEN   = "92"
    FGBRIGHTYELLOW  = "93"
    FGBRIGHTBLUE    = "94"
    FGBRIGHTMAGENTA = "95"
    FGBRIGHTCYAN    = "96"
    FGBRIGHTWHITE   = "97"

    BGBRIGHTBLACK   = "100"
    BGBRIGHTRED     = "101"
    BGBRIGHTGREEN   = "102"
    BGBRIGHTYELLOW  = "103"
    BGBRIGHTBLUE    = "104"
    BGBRIGHTMAGENTA = "105"
    BGBRIGHTCYAN    = "106"
    BGBRIGHTWHITE   = "107"

def _cprint(fg: _EAnsiColours, bg: _EAnsiColours, text: str):
    print(f"\033[{fg.value};{bg.value}m{text}\033[{_EAnsiColours.FGWHITE.value};{_EAnsiColours.BGBLACK.value}m")

def printred(text: str):
    _cprint(_EAnsiColours.FGRED, _EAnsiColours.BGBLACK, text)

def printgreen(text: str):
    _cprint(_EAnsiColours.FGGREEN, _EAnsiColours.BGBLACK, text)
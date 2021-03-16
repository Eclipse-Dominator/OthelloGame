from collections import namedtuple
from typing import NamedTuple
import enum


class Move(namedtuple("Move", ["player", "point"])):
    def __str__(self):
        return f"{str(self.player)}: {str(self.point)}"


class Point(namedtuple("Point", ["x", "y"])):
    def __str__(self):
        return f"{chr(self.x+97)}{self.y+1}"


class State(enum.Enum):
    Empty = 0
    Black = 1
    White = 2

    @ property
    def opposite(self):
        if self is State.Empty:
            return self
        return State.Black if self is State.White else State.White

    def __str__(self):
        if self is State.White:
            return "w"
        if self is State.Black:
            return "b"
        return " "

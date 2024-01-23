from enum import Enum, auto


class MenuEvent(Enum):
    CLOSE = auto()
    LOAD_SQL = auto()
    SAVE_SQL = auto()
    SAVE_RESULT = auto()
    EXIT = auto()

from enum import Enum, IntEnum, auto

class EquipmentType(Enum):
    EMPTY = auto()
    LEFT_BELT = auto()
    RIGHT_BELT = auto()
    UP_BELT = auto()
    DOWN_BELT = auto()
    MINE = auto()
    FURNACE = auto()
    PAPERCLIP_MACHINE = auto()

class ResourceType(IntEnum):
    COAL_DEPOSIT = 0
    IRON_DEPOSIT = 1
    COAL_ORE = 2
    IRON_ORE = 3
    STEEL = 4
    PAPERCLIP = 5
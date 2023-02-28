from enum import Enum, auto

class FactoryEquipment(Enum):
    EMPTY = auto()
    LEFT_BELT = auto()
    RIGHT_BELT = auto()
    UP_BELT = auto()
    DOWN_BELT = auto()
    MINE = auto()
    FURNACE = auto()
    PAPERCLIP_MACHINE = auto()

class FactoryResource(Enum):
    EMPTY = auto()
    COAL_DEPOSIT = auto()
    IRON_DEPOSIT = auto()
    COAL_ORE = auto()
    IRON_ORE = auto()
    STEEL = auto()
    PAPERCLIP = auto()
from .types import EquipmentType, ResourceType
from .equipment import Equipment, Belt, Mine, Furnace
import numpy as np
from typing import Optional

class Factory:
    def __init__(self, cursor_pos=(0, 0), map_size=(64, 64)):
        self._x = cursor_pos[0]
        self._y = cursor_pos[1]
        self._map_size = map_size

        self._resources = np.zeros((map_size[0], map_size[1], len(ResourceType)), dtype=np.float32)        
        self._resource_amts = {}

        self._equipment = []
        self._equipment_map = [[EquipmentType.EMPTY for _ in range(map_size[1])] for _ in range(map_size[0])]

    def move_cursor(self, dx=0, dy=0):
        if self._x + dx < self._map_size[0] and self._x + dx >= 0: self._x += dx
        if self._y + dy < self._map_size[1] and self._y + dy >= 0: self._y += dy

    def get_cursor(self) -> tuple[int, int]:
        return (self._x, self._y)

    def get_equipment(self, x: int, y: int) -> EquipmentType:
        return self._equipment_map[x][y]

    def build_equipment(self, type: EquipmentType, pos: Optional[tuple[int, int]] = None):
        x = pos[0] if pos else self._x
        y = pos[1] if pos else self._y
        if self._equipment_map[x][y] != EquipmentType.EMPTY:
            return
        
        self._equipment_map[x][y] = type
        if type == EquipmentType.LEFT_BELT or type == EquipmentType.RIGHT_BELT:
            if x == 0 or x == self._map_size[0]-1: return
            self._equipment.append(Belt((x, y), type))
        elif type == EquipmentType.UP_BELT or type == EquipmentType.DOWN_BELT:
            if y == 0 or y == self._map_size[1]-1: return
            self._equipment.append(Belt((x, y), type))
        elif type == EquipmentType.MINE:
            self._equipment.append(Mine((x, y)))
        elif type == EquipmentType.FURNACE:
            self._equipment.append(Furnace((x, y)))
        else:
            raise ValueError("Invalid equipment type")

    def destroy_equipment(self, pos: Optional[tuple[int, int]] = None):
        x = pos[0] if pos else self._x
        y = pos[1] if pos else self._y
        if self._equipment_map[x][y] == EquipmentType.EMPTY:
            return

        self._equipment_map[x][y] = EquipmentType.EMPTY
        for equipment in self._equipment:
            if equipment.pos == (x, y):
                self._equipment.remove(equipment)
                break

    def get_resources(self, x: int, y: int) -> dict[ResourceType, int]:
        resources = {}
        for i in range(len(ResourceType)):
            resources[ResourceType(i)] = self._resources[x, y, i]
        return resources

    def get_resource_amt(self, resource: ResourceType) -> int:
        return self._resource_amts.get(resource, 0)
    
    def add_resource(self, x: int, y: int, resource: ResourceType, amt: int):
        self._resources[x, y, resource] = amt
        self._resource_amts[resource] = self._resource_amts.get(resource, 0) + amt

    def step(self) -> dict[ResourceType, int]:
        """Computes next step in resource flow and returns increases in resources"""
        old_resources = np.copy(self._resources)
        new_resources = {}
        for equipment in self._equipment:
            in_flow, out_flow = equipment.process(old_resources[equipment.input])
            self._resources[equipment.output] += out_flow
            self._resources[equipment.input] -= in_flow
            old_resources[equipment.input] -= in_flow
        return new_resources

    def reset(self, cursor: tuple[int, int] = (0, 0)):
        self._x, self._y = cursor
        self._equipment_map = [[EquipmentType.EMPTY for _ in range(self._map_size[1])] for _ in range(self._map_size[0])]
        self._resource_map = [[{} for _ in range(self._map_size[1])] for _ in range(self._map_size[0])]
        self._resource_flows = []
        self._resource_amts = {} 
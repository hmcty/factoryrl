from .data import FactoryEquipment, FactoryResource

class Factory:
    def __init__(self, cursor_pos=(0, 0), map_size=(64, 64)):
        self._x = cursor_pos[0]
        self._y = cursor_pos[1]
        self._map_size = map_size
        
        self._equipment_map = [[FactoryEquipment.EMPTY for _ in range(map_size[1])] for _ in range(map_size[0])]
        self._resource_map = [[{} for _ in range(map_size[1])] for _ in range(map_size[0])]
        self._resource_flows = []
        self._resource_amts = {}

    def move_cursor(self, dx=0, dy=0):
        if self._x + dx < self._map_size[0] and self._x + dx >= 0: self._x += dx
        if self._y + dy < self._map_size[1] and self._y + dy >= 0: self._y += dy

    def get_cursor(self) -> tuple[int, int]:
        return (self._x, self._y)

    def get_equipment(self, x: int, y: int) -> FactoryEquipment:
        return self._equipment_map[x][y]

    def get_resources(self, x: int, y: int) -> dict[FactoryResource, int]:
        return self._resource_map[x][y]

    def get_resource_amt(self, resource: FactoryResource) -> int:
        return self._resource_amts.get(resource, 0)
    
    def add_resource(self, x: int, y: int, resource: FactoryResource, amt: int):
        self._resource_map[x][y][resource] = amt
        self._resource_amts[resource] = self._resource_amts.get(resource, 0) + amt

    def build_equipment(self, equipment: FactoryEquipment):
        """Builds equipment at current cursor position and adds any necessary flows"""
        if self._equipment_map[self._x][self._y] != FactoryEquipment.EMPTY:
            return

        self._equipment_map[self._x][self._y] = equipment        
        match equipment:
            case FactoryEquipment.RIGHT_BELT:
                self.add_belt_flow((self._x-1, self._y), (self._x, self._y))
                self.add_belt_flow((self._x, self._y), (self._x+1, self._y))
            case FactoryEquipment.LEFT_BELT:
                self.add_belt_flow((self._x+1, self._y), (self._x, self._y))
                self.add_belt_flow((self._x, self._y), (self._x-1, self._y))
            case FactoryEquipment.DOWN_BELT:
                self.add_belt_flow((self._x, self._y-1), (self._x, self._y))
                self.add_belt_flow((self._x, self._y), (self._x, self._y+1))
            case FactoryEquipment.UP_BELT:
                self.add_belt_flow((self._x, self._y+1), (self._x, self._y))
                self.add_belt_flow((self._x, self._y), (self._x, self._y-1))
            case FactoryEquipment.MINE:
                self.add_alchemy_flow((self._x, self._y), FactoryResource.COAL_DEPOSIT, FactoryResource.COAL_ORE)
                self.add_alchemy_flow((self._x, self._y), FactoryResource.IRON_DEPOSIT, FactoryResource.IRON_ORE)
            case FactoryEquipment.FURNACE:
                self.add_alchemy_flow((self._x, self._y), FactoryResource.IRON_ORE, FactoryResource.STEEL)
            case FactoryEquipment.PAPERCLIP_MACHINE:
                self.add_alchemy_flow((self._x, self._y), FactoryResource.STEEL, FactoryResource.PAPERCLIP) 
        
    def add_belt_flow(self, a: tuple[int, int], b: tuple[int, int], cap: int = 100):
        """Creates a flow of moveable resources between two points"""
        if a[0] < 0 or a[0] >= self._map_size[0]: return
        if a[1] < 0 or a[1] >= self._map_size[1]: return
        if b[0] < 0 or b[0] >= self._map_size[0]: return
        if b[1] < 0 or b[1] >= self._map_size[1]: return
        self._resource_flows.append(((FactoryResource.COAL_ORE,) + a, (FactoryResource.COAL_ORE,) + b, cap))
        self._resource_flows.append(((FactoryResource.IRON_ORE,) + a, (FactoryResource.IRON_ORE,) + b, cap))
        self._resource_flows.append(((FactoryResource.STEEL,) + a, (FactoryResource.STEEL,) + b, cap))
        self._resource_flows.append(((FactoryResource.PAPERCLIP,) + a, (FactoryResource.PAPERCLIP,) + b, cap))

    def add_alchemy_flow(self, pnt: tuple[int, int], a_type: FactoryResource, b_type: FactoryResource, cap: int = 100):
        """
        Creates a flow between two resources at the same point
        TODO: Allow multiple input resources
        """
        self._resource_flows.append(((a_type,) + pnt, (b_type,) + pnt, cap))

    def step(self) -> dict[FactoryResource, int]:
        """Computes next step in resource flow and returns increases in resources"""
        new_resources = {}
        for flow in self._resource_flows:
            start, end, amt = flow
            start_type, start_x, start_y = start
            end_type, end_x, end_y = end

            start_resource = self._resource_map[start_x][start_y]
            end_resource = self._resource_map[end_x][end_y]
            if start_type in start_resource:
                start_amt = start_resource[start_type]
                end_amt = end_resource.get(end_type, 0)
                if start_amt == 0:
                    continue
                elif start_amt < amt:
                    amt = start_amt

                self._resource_map[start_x][start_y][start_type] -= amt
                self._resource_map[end_x][end_y][end_type] = end_amt + amt

                if start_type != end_type:
                    self._resource_amts[start_type] -= amt
                    self._resource_amts[end_type] = self._resource_amts.get(end_type, 0) + amt
                    new_resources[end_type] = new_resources.get(end_type, 0) + amt
        return new_resources

    def reset(self, cursor: tuple[int, int] = (0, 0)):
        self._x, self._y = cursor
        self._equipment_map = [[FactoryEquipment.EMPTY for _ in range(self._map_size[1])] for _ in range(self._map_size[0])]
        self._resource_map = [[{} for _ in range(self._map_size[1])] for _ in range(self._map_size[0])]
        self._resource_flows = []
        self._resource_amts = {} 
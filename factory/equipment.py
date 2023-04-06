from .types import EquipmentType, ResourceType
import numpy as np

class Equipment:
    @property
    def input(self):
        """Map index to get resource inputs."""
        return self._input

    @property
    def output(self):
        """Map index to get resource outputs."""
        return self._output

    def process(self, input: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Processes input resources and returns the input and output flows."""
        raise NotImplementedError

class Belt(Equipment):

    moveable_resources = (
        int(ResourceType.COAL_ORE), int(ResourceType.IRON_ORE),
        int(ResourceType.STEEL), int(ResourceType.PAPERCLIP)
    )

    def __init__(self, pos: tuple[int, int], type: EquipmentType):
        x, y = pos
        self._output = (x, y, self.moveable_resources)
        self._flow = np.full((len(self.moveable_resources),), 25.0, dtype=np.float32)
        if type == EquipmentType.LEFT_BELT:
            self._input = (x+1, y, self.moveable_resources)
        elif type == EquipmentType.RIGHT_BELT:
            self._input = (x-1, y, self.moveable_resources)
        elif type == EquipmentType.UP_BELT:
            self._input = (x, y+1, self.moveable_resources)
        elif type == EquipmentType.DOWN_BELT:
            self._input = (x, y-1, self.moveable_resources)
        else:
            raise ValueError("Invalid belt type")

    def process(self, block: np.ndarray):
        flow = np.minimum(self._flow, block)
        return flow, flow

class Mine(Equipment):

    def __init__(self, pos: tuple[int, int]):
        self._input = pos + ((ResourceType.COAL_DEPOSIT, ResourceType.IRON_DEPOSIT),)
        self._output = pos + ((ResourceType.COAL_ORE, ResourceType.IRON_ORE),)
        self._flow = np.array([50.0, 50.0], dtype=np.float32)

    def process(self, block: np.ndarray):
        flow = np.minimum(self._flow, block)
        return flow, flow

class Furnace(Equipment):

    def __init__(self, pos: tuple[int, int]):
        x, y = pos
        self._input = (slice(x-1, x+2), slice(y-1, y+2), 
            (ResourceType.COAL_ORE, ResourceType.IRON_ORE))
        self._output = pos + ((ResourceType.STEEL),)
        self._flow = np.array([25.0, 50.0], dtype=np.float32)

        self.is_cooking = False 
        self._time_left = 0

    def process(self, input: np.ndarray):
        """If not cooking, pool together """
        if self.is_cooking:
            self._time_left -= 1
            if self._time_left == 0:
                self.is_cooking = False
                return np.zeros_like(input), 1.0
            else:
                return np.zeros_like(input), 0.0
        else:
            input_flow = np.zeros_like(input)
            coal_input = np.where(input[:, :, 0] > 2.0)
            iron_input = np.where(input[:, :, 1] > 1.0)
            if len(coal_input[0]) > 0 and len(iron_input[0]) > 0:
                input_flow[coal_input[0][0], coal_input[1][0], 0] = 2.0
                input_flow[iron_input[0][0], iron_input[1][0], 1] = 1.0
                self.is_cooking = True
                self._time_left = 3
            return input_flow, 0.0
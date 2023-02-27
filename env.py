import gymnasium as gym
import numpy as np
from enum import Enum, auto
import random
from PIL import Image

class FactoryAction(Enum):
    MOVE_CURSOR_LEFT = auto()
    MOVE_CURSOR_RIGHT = auto()
    MOVE_CURSOR_UP = auto()
    MOVE_CURSOR_DOWN = auto()
    BUILD_LEFT_BELT = auto()
    BUILD_RIGHT_BELT = auto()
    BUILD_UP_BELT = auto()
    BUILD_DOWN_BELT = auto()
    BUILD_MINE = auto()
    BUILD_FURNACE = auto()
    BUILD_PAPERCLIP_MACHINE = auto()
    WAIT = auto()

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

class Factory(gym.Env):
    def __init__(self, map_size=(64, 64), obs_size=(64, 64), max_steps=10000):
        self._map_size = map_size
        self._obs_size = obs_size
        self._max_steps = max_steps

        self._step = 0
        self._map = [[FactoryEquipment.EMPTY for _ in range(map_size[1])] for _ in range(map_size[0])]
        self._resources = [[{} for _ in range(map_size[1])] for _ in range(map_size[0])]
        for x in range(map_size[0]):
            for y in range(map_size[1]):
                if random.random() < 0.10:
                    self._resources[x][y][FactoryResource.COAL_DEPOSIT] = 1000
                elif random.random() < 0.10:
                    self._resources[x][y][FactoryResource.IRON_DEPOSIT] = 1000
        self._resource_flows = []
        self._x = map_size[0]//2
        self._y = map_size[1]//2

    @property
    def observation_space(self):
        return gym.spaces.Box(low=0, high=255, shape=self._obs_size + (3,))

    @property
    def action_space(self):
        return gym.spaces.Discrete(len(FactoryAction))

    def step(self, action: gym.spaces.Discrete):
        self._step += 1
        if action == FactoryAction.MOVE_CURSOR_LEFT:
            self._x -= 1
        elif action == FactoryAction.MOVE_CURSOR_RIGHT:
            self._x += 1
        elif action == FactoryAction.MOVE_CURSOR_UP:
            self._y -= 1
        elif action == FactoryAction.MOVE_CURSOR_DOWN:
            self._y += 1
        elif action == FactoryAction.BUILD_LEFT_BELT:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.LEFT_BELT
                self._add_belt_flow((self._x+1, self._y), (self._x, self._y))
        elif action == FactoryAction.BUILD_RIGHT_BELT:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.RIGHT_BELT
                self._add_belt_flow((self._x-1, self._y), (self._x, self._y))
        elif action == FactoryAction.BUILD_UP_BELT:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.UP_BELT
                self._add_belt_flow((self._x, self._y-1), (self._x, self._y))
        elif action == FactoryAction.BUILD_DOWN_BELT:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.DOWN_BELT
                self._add_belt_flow((self._x, self._y+1), (self._x, self._y))
        elif action == FactoryAction.BUILD_MINE:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.MINE
                self._add_alchemy_flow((self._x, self._y), FactoryResource.COAL_DEPOSIT, FactoryResource.COAL_ORE)
                self._add_alchemy_flow((self._x, self._y), FactoryResource.IRON_DEPOSIT, FactoryResource.IRON_ORE)
        elif action == FactoryAction.BUILD_FURNACE:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.FURNACE
                # TODO: Add coal consumption
                self._add_alchemy_flow((self._x, self._y), FactoryResource.IRON_ORE, FactoryResource.STEEL)
        elif action == FactoryAction.BUILD_PAPERCLIP_MACHINE:
            if self._map[self._x][self._y] == FactoryEquipment.EMPTY:
                self._map[self._x][self._y] = FactoryEquipment.PAPERCLIP_MACHINE
                self._add_alchemy_flow((self._x, self._y), FactoryResource.STEEL, FactoryResource.PAPERCLIP)
        elif action == FactoryAction.WAIT:
            pass
        else:
            raise ValueError("Invalid action")

        reward = self._step_resources() 
        obs = self._create_observation()
        done = self._step >= self._max_steps
        return obs, reward, done, {}

    def _step_resources(self) -> float:
        reward = 0.0
        for flow in self._resource_flows:
            start, end, amt = flow
            start_type, start_x, start_y = start
            end_type, end_x, end_y = end

            start_resource = self._resources[start_x][start_y]
            end_resource = self._resources[start_x][start_y]
            if start_type in start_resource:
                start_amt = start_resource[start_type]
                end_amt = end_resource.get(end_type, 0)
                if start_amt == 0:
                    continue
                elif start_amt < amt:
                    amt = start_amt

                self._resources[start_x][start_y][start_type] -= amt
                self._resorces[end_x][end_y][end_type] = end_amt + amt

                if end_type == FactoryResource.PAPERCLIP:
                    reward += (2.0 * amt)
                elif end_type == FactoryResource.STEEL:
                    reward += (0.5 * amt)
                elif end_type == FactoryResource.IRON_ORE or end_type == FactoryResource.COAL_ORE:
                    reward += (0.1 * amt)
        return reward

    def _add_belt_flow(self, start, end):
        self._resource_flows.append(
            ((FactoryResource.COAL_ORE,) + start, (FactoryResource.COAL_ORE,) + end, 100),
            ((FactoryResource.IRON_ORE,) + start, (FactoryResource.IRON_ORE,) + end, 100),
            ((FactoryResource.STEEL,) + start, (FactoryResource.STEEL,) + end, 100),
            ((FactoryResource.PAPERCLIP,) + start, (FactoryResource.PAPERCLIP,) + end, 100),
        )
    
    def _add_alchemy_flow(self, pos, start_resource, end_resource):
        self._resource_flows.append(
            ((start_resource,) + pos, (end_resource,) + pos, 100),
        )

    def _create_observation(self) -> gym.spaces.Box:
        start_x = 
        if self._x < 4

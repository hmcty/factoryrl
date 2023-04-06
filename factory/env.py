import gymnasium as gym
from enum import Enum, auto
import numpy as np
import cv2
import os
from perlin_noise import PerlinNoise
import random

from .factory import Factory
from .types import EquipmentType, ResourceType

class FactoryAction(Enum):
    MOVE_CURSOR_LEFT = 0
    MOVE_CURSOR_RIGHT = 1
    MOVE_CURSOR_UP = 2
    MOVE_CURSOR_DOWN = 3
    BUILD_LEFT_BELT = 4
    BUILD_RIGHT_BELT = 5
    BUILD_UP_BELT = 6
    BUILD_DOWN_BELT = 7
    BUILD_MINE = 8
    BUILD_FURNACE = 9
    BUILD_PAPERCLIP_MACHINE = 10
    DESTROY_EQUIPMENT = 11
    WAIT = 12

class FactoryEnv(gym.Env):
    def __init__(self, map_size=(64, 64), obs_size=(64, 64), max_steps=10000):
        self._map_size = map_size 
        self._obs_size = obs_size

        cursor_pos = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        self._factory = Factory(cursor_pos=cursor_pos, map_size=map_size)
        self._step = 0
        self._max_steps = max_steps

        self._assets = {}
        for asset in os.listdir("assets"):
            img = cv2.imread(os.path.join("assets", asset), cv2.IMREAD_UNCHANGED)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            img = cv2.flip(img, 1)
            self._assets[asset] = img

        # Generate random terrain
        coal_noise = PerlinNoise(octaves=6, seed=0)
        iron_noise = PerlinNoise(octaves=6, seed=1)
        for x in range(map_size[0]):
            for y in range(map_size[1]):
                coal = coal_noise([x / 64, y / 64])
                if coal > 0.2:
                    self._factory.add_resource(x, y, ResourceType.COAL_DEPOSIT, 1000)
                iron = iron_noise([x / 64, y / 64])
                if iron > 0.3:
                    self._factory.add_resource(x, y, ResourceType.IRON_DEPOSIT, 1000)

    @property
    def observation_space(self):
        """Returns a image of factory w.r.t. cursor position"""
        return gym.spaces.Box(low=0, high=255, shape=self._obs_size + (3,), dtype=np.uint8)

    @property
    def action_space(self):
        """Modifies factory w.r.t. cursor position"""
        return gym.spaces.Discrete(len(FactoryAction))

    def step(self, action: int):
        # Step internal engine
        self._step += 1
        
        action = FactoryAction(action)
        if action == FactoryAction.MOVE_CURSOR_LEFT:
            self._factory.move_cursor(dx=-1)
        elif action == FactoryAction.MOVE_CURSOR_RIGHT:
            self._factory.move_cursor(dx=1)
        elif action == FactoryAction.MOVE_CURSOR_UP:
            self._factory.move_cursor(dy=-1)
        elif action == FactoryAction.MOVE_CURSOR_DOWN:
            self._factory.move_cursor(dy=1)
        elif action == FactoryAction.BUILD_LEFT_BELT:
            self._factory.build_equipment(EquipmentType.LEFT_BELT)
        elif action == FactoryAction.BUILD_RIGHT_BELT:
            self._factory.build_equipment(EquipmentType.RIGHT_BELT)
        elif action == FactoryAction.BUILD_UP_BELT:
            self._factory.build_equipment(EquipmentType.UP_BELT)
        elif action == FactoryAction.BUILD_DOWN_BELT:
            self._factory.build_equipment(EquipmentType.DOWN_BELT)
        elif action == FactoryAction.BUILD_MINE:
            self._factory.build_equipment(EquipmentType.MINE)
        elif action == FactoryAction.BUILD_FURNACE:
            self._factory.build_equipment(EquipmentType.FURNACE)
        elif action == FactoryAction.BUILD_PAPERCLIP_MACHINE:
            self._factory.build_equipment(EquipmentType.PAPERCLIP_MACHINE)
        elif action == FactoryAction.DESTROY_EQUIPMENT:
            self._factory.destroy_equipment()
        elif action == FactoryAction.WAIT:
            pass

        new_resources = self._factory.step()
        reward = new_resources.get(ResourceType.PAPERCLIP, 0.0) * 2.0
        reward += new_resources.get(ResourceType.STEEL, 0.0) * 0.5
        reward += new_resources.get(ResourceType.IRON_ORE, 0.0) * 0.1
        reward += new_resources.get(ResourceType.COAL_ORE, 0.0) * 0.1
        obs = self.observe()
        done = self._step >= self._max_steps

        x, y = self._factory.get_cursor()
        info = {
            'resources': self._factory.get_resources(x, y),
        }

        return obs, reward, done, info

    def reset(self):
        self._step = 0
        cursor_pos = (random.randint(0, self._map_size[0] - 1), random.randint(0, self._map_size[1] - 1))
        self._factory.reset(cursor=cursor_pos)
        coal_noise = PerlinNoise(octaves=6)
        iron_noise = PerlinNoise(octaves=6)
        for x in range(self._map_size[0]):
            for y in range(self._map_size[1]):
                coal = coal_noise([x / 64, y / 64])
                if coal > 0.2:
                    self._factory.add_resource(x, y, ResourceType.COAL_DEPOSIT, 250)
                iron = iron_noise([x / 64, y / 64])
                if iron > 0.2:
                    self._factory.add_resource(x, y, ResourceType.IRON_DEPOSIT, 250)
        return self.observe()

    def observe(self) -> np.ndarray:
        obs = np.full((self._obs_size[0], self._obs_size[1], 3), 255, dtype=np.uint8)
        def set_block(x, y, img):
            bg = obs[x*8:(x+1)*8, y*8:(y+1)*8, :].astype(np.float32)
            fg = img.astype(np.float32)
            alpha = fg[:, :, 3] / 255.0
            for c in range(3):
                obs[x*8:(x+1)*8, y*8:(y+1)*8, c] = ((1.0 - alpha) * bg[:, :, c]) + (alpha * fg[:, :, c])
        
        cursor = self._factory.get_cursor()
        map_roi = (min(max(0, cursor[0]-4), self._map_size[0]-8),
            min(max(0, cursor[1]-4), self._map_size[1]-8))
        for x in range(8):
            for y in range(8):
                resources = self._factory.get_resources(map_roi[0] + x, map_roi[1] + y)
                if resources.get(ResourceType.COAL_DEPOSIT, 0) > 0:
                    set_block(x, y, self._assets["coal_deposit.png"])
                if resources.get(ResourceType.IRON_DEPOSIT, 0) > 0:
                    set_block(x, y, self._assets["iron_deposit.png"])

                equipment = self._factory.get_equipment(map_roi[0] + x, map_roi[1] + y)
                if equipment == EquipmentType.EMPTY:
                    pass
                elif equipment == EquipmentType.LEFT_BELT:
                    set_block(x, y, self._assets["left_belt.png"])
                elif equipment == EquipmentType.RIGHT_BELT:
                    set_block(x, y, self._assets["right_belt.png"])
                elif equipment == EquipmentType.UP_BELT:
                    set_block(x, y, self._assets["up_belt.png"])
                elif equipment == EquipmentType.DOWN_BELT:
                    set_block(x, y, self._assets["down_belt.png"])

                if resources.get(ResourceType.COAL_ORE, 0) > 0:
                    set_block(x, y, self._assets["coal_deposit.png"])
                if resources.get(ResourceType.IRON_ORE, 0) > 0:
                    set_block(x, y, self._assets["iron_deposit.png"])

                if equipment == EquipmentType.MINE:
                    set_block(x, y, self._assets["mine.png"])
                elif equipment == EquipmentType.FURNACE:
                    set_block(x, y, self._assets["furnace.png"])

        obs_cursor_x = cursor[0] - map_roi[0]
        obs_cursor_y = cursor[1] - map_roi[1] 
        set_block(obs_cursor_x, obs_cursor_y, self._assets["cursor.png"])

        return obs

    def render(self, *args):
        obs = self.observe()
        obs.astype(np.float32)
        img = cv2.resize(obs, (512, 512), interpolation=cv2.INTER_NEAREST)
        return img

from __future__ import annotations
from typing import TYPE_CHECKING

import math
import pygame
import constants

if TYPE_CHECKING:
    from player import Player


class Camera:
    def __init__(self):
        self.yaw    = 0.0
        self.pitch  = 0.0
        
        
    def update(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.add_yaw(event.rel[0] * constants.Camera.SENSITIVITY_X)
                self.add_pitch(event.rel[1] * constants.Camera.SENSITIVITY_Y)


    def add_yaw(self, dx):
        self.yaw += dx


    def add_pitch(self, dy):
        self.pitch += dy
        self.pitch = max(-constants.Camera.PITCH_LIMIT, min(constants.Camera.PITCH_LIMIT, self.pitch))


    def horizon_y(self, player: Player):
        hy = constants.Game.SCREEN_HEIGHT_HALF + int(player.cam_z * 0.75) - int(self.pitch)
        return max(2, min(constants.Game.SCREEN_HEIGHT - 2, hy))


    @staticmethod
    def cast_ray(px, py, angle):
        from game import Game
        
        sa, ca = math.sin(angle), math.cos(angle)

        h_dist = 1e30
        if sa != 0:
            step_y = constants.Map.TILE if sa > 0 else -constants.Map.TILE
            y_h = (int(py/constants.Map.TILE)+(1 if sa>0 else 0))*constants.Map.TILE - (0 if sa>0 else 1e-6)
            x_h = px + (y_h - py) / sa * ca
            dy_h = step_y;  dx_h = dy_h / sa * ca
            for _ in range(constants.Map.MAX_STEPS):
                if Game.get().map.is_wall(x_h, y_h):
                    h_dist = math.hypot(x_h-px, y_h-py)
                    break
                x_h += dx_h;  y_h += dy_h

        v_dist = 1e30
        if ca != 0:
            step_x = constants.Map.TILE if ca > 0 else -constants.Map.TILE
            x_v = (int(px/constants.Map.TILE)+(1 if ca>0 else 0))*constants.Map.TILE - (0 if ca>0 else 1e-6)
            y_v = py + (x_v - px) / ca * sa
            dx_v = step_x;  dy_v = dx_v / ca * sa
            for _ in range(constants.Map.MAX_STEPS):
                if Game.get().map.is_wall(x_v, y_v):
                    v_dist = math.hypot(x_v-px, y_v-py)
                    break
                x_v += dx_v;  y_v += dy_v

        is_horiz = h_dist < v_dist
        return (h_dist if is_horiz else v_dist), is_horiz
      
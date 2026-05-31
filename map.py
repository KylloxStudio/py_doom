from __future__ import annotations
from typing import TYPE_CHECKING
    
import math
import pygame
import constants

if TYPE_CHECKING:
    from player import Player


class Map:
    def __init__(self):
        self.data = [
            "1111111111111111111",
            "1000000000000000001",
            "1011100001110000001",
            "1010000000010000001",
            "1010111100010111001",
            "1000100000000001001",
            "1000100011000001001",
            "1000000011000000001",
            "1001110000011100001",
            "1000000000000000001",
            "1011000110000110001",
            "1001000010000010001",
            "1001111010001010001",
            "1000000010000000001",
            "1000000000000000001",
            "1111111111111111111",
        ]
        
        self.width = len(self.data[0])
        self.height = len(self.data)
        
        self.z_buffer = [0.0] * constants.Camera.NUM_RAYS
        
        
    def draw_walls(self, buf: pygame.Surface, player: Player, hy: int):
        from camera import Camera
        
        ray_angle = player.angle - constants.Camera.HALF_FOV
        for col in range(constants.Camera.NUM_RAYS):
            a = ray_angle % (2 * math.pi)
            dist, is_horiz = Camera.cast_ray(player.x, player.y, a)
            dist = max(0.1, dist * math.cos(player.angle - a))
            
            self.z_buffer[col] = dist

            wall_h = min(constants.Game.SCREEN_HEIGHT * 2, int(constants.Map.TILE * constants.Camera.PROJ_DIST / dist))
            y0     = hy - wall_h // 2

            bright = max(30, min(255, int(220 * constants.Map.TILE / (dist + 1))))
            shade  = int(bright * (0.5 if is_horiz else 1.0))
            color  = (shade // 2, shade // 2, shade // 2)
            pygame.draw.rect(buf, color, (col, y0, 1, wall_h))
            ray_angle += constants.Camera.DELTA_ANGLE
    
    
    def is_wall(self, x, y):
        mx, my = int(x / constants.Map.TILE), int(y / constants.Map.TILE)
        if 0 <= mx < self.width and 0 <= my < self.height:
            return self.data[my][mx] == "1"
        return True

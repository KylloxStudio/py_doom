from __future__ import annotations
from typing import TYPE_CHECKING

import math
import random
import pygame
import constants

if TYPE_CHECKING:
    from player import Player


class Enemy:
    _sprite      = None
    _sprite_dead = None
    
    
    @classmethod
    def _get_sprite(cls) -> pygame.Surface:
        if cls._sprite is None:
            cls._sprite = pygame.image.load(constants.Enemy.SPRITE_PATH).convert_alpha()
        return cls._sprite


    @classmethod
    def _get_sprite_dead(cls) -> pygame.Surface:
        if cls._sprite_dead is None:
            cls._sprite_dead = pygame.image.load(constants.Enemy.SPRITE_DEAD_PATH).convert_alpha()
        return cls._sprite_dead


    def __init__(self, x: float, y: float):
        self.los = False
        
        self.x = float(x)
        self.y = float(y)
        
        self.max_hp = constants.Enemy.MAX_HP
        self.cur_hp = constants.Enemy.MAX_HP
        
        self.sight_dist = constants.Enemy.SIGHT_DIST
        
        self.move_speed = constants.Enemy.MOVE_SPEED
        
        self.attack_damage_min = constants.Enemy.ATTACK_DAMAGE_MIN
        self.attack_damage_max = constants.Enemy.ATTACK_DAMAGE_MAX
        self.attack_dist   = constants.Enemy.ATTACK_DIST
        self.attack_cool   = constants.Enemy.ATTACK_COOL

        self.state = constants.Enemy.STATE_IDLE
        
        self._attack_timer = 0.0
        self._anim_tick    = 0.0
        self._walk_offset  = 0.0   # 걷기 bob
        
    
    @property
    def attack_damage(self):
        return random.randint(self.attack_damage_min, self.attack_damage_max)


    def update(self, player: Player, dt: float):
        if self.state == constants.Enemy.STATE_DEAD: return
        
        self.los = self._has_los(player)

        self._attack_timer  = max(self._attack_timer - dt, 0.0)
        self._anim_tick    += dt

        dx   = player.x - self.x
        dy   = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.attack_dist and self.los:
            self.state = constants.Enemy.STATE_ATTACK
            self._walk_offset *= 0.9
            if self._attack_timer <= 0:
                player.take_damage(self.attack_damage)
                self._attack_timer = self.attack_cool
                
        elif dist < self.sight_dist:
            self.state = constants.Enemy.STATE_CHASE
            self._walk_offset = math.sin(self._anim_tick * 8.0) * 3.0
            self._move_toward(dx, dy, dist)
            
        else:
            self.state = constants.Enemy.STATE_IDLE
            self._walk_offset *= 0.8


    def _move_toward(self, dx: float, dy: float, dist: float):        
        if dist < 0.001: return
        
        from game import Game
        
        map = Game.get().map
        nx = dx / dist * self.move_speed
        ny = dy / dist * self.move_speed
        margin = 16
        
        if not map.is_wall(self.x + nx + math.copysign(margin, nx), self.y): self.x += nx
        if not map.is_wall(self.x, self.y + ny + math.copysign(margin, ny)): self.y += ny


    def take_damage(self, player: Player, dmg: int):
        if self.is_dead:
            return
        
        self.cur_hp -= dmg
        if self.cur_hp <= 0:
            self.death()
            player.killed_enemy(self)


    def death(self):
        self.cur_hp = 0
        self.state  = constants.Enemy.STATE_DEAD
        
        import random
        from sound import Sound
        Sound.play(random.choice(constants.Sound.ENEMY_DEATH_PATHS), constants.Sound.ENEMY_DEATH_VOLUME)
    
        
    def _has_los(self, player: Player) -> bool:
        """플레이어 → 적 사이에 벽이 없는지 확인."""
        from game import Game

        dx   = self.x - player.x
        dy   = self.y - player.y
        dist = math.hypot(dx, dy)
        
        if dist < 1: return True

        # TILE//4 간격으로 레이 스텝
        steps = max(4, min(int(dist / (constants.Map.TILE // 4)), 40))
        for i in range(1, steps):
            t  = i / steps
            cx = player.x + dx * t
            cy = player.y + dy * t
            if Game.get().map.is_wall(cx, cy): return False
            
        return True


    @property
    def is_dead(self) -> bool:
        return self.state == constants.Enemy.STATE_DEAD


    # ── 스프라이트 렌더링 ────────────────────────────────────────────
    def draw(self, buf: pygame.Surface, player: Player, z_buffer: list[float], hy: int):
        NR = constants.Camera.NUM_RAYS
        SH = constants.Game.SCREEN_HEIGHT
        
        dx   = self.x - player.x
        dy   = self.y - player.y
        dist = math.hypot(dx, dy)
        
        if dist < 1: return

        angle_to  = math.atan2(dy, dx)
        rel_angle = (angle_to - player.angle + math.pi) % (2 * math.pi) - math.pi

        if abs(rel_angle) > constants.Camera.HALF_FOV + 0.3: return

        # 크기 계산
        corrected = max(0.5, dist * math.cos(rel_angle))
        sprite_h  = int(constants.Map.TILE * constants.Camera.PROJ_DIST / corrected * constants.Enemy.SCALE_FACTOR)
        sprite_h  = min(sprite_h, constants.Game.SCREEN_HEIGHT * 2)
        
        cx = int((0.5 + rel_angle / constants.Camera.FOV) * NR)

        if self.is_dead:
            sprite_h //= 4
            sprite_w = sprite_h * 2
        else:
            sprite_h = int(sprite_h + self._walk_offset)
            sprite_w = int(sprite_h * 0.5)

        if sprite_w < 1 or sprite_h < 1: return

        src = self._get_sprite_dead() if self.is_dead else self._get_sprite()
        scaled = pygame.transform.scale(src, (sprite_w, sprite_h))

        # 거리 기반 어둠 오버레이
        # shade = max(0, min(200, int(200 * constants.Map.TILE / (corrected + 1))))
        # if shade < 200:
        #     dark = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
        #     dark.fill((0, 0, 0, 220 - shade))
        #     scaled.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        shade = max(80, min(255, int(255 * constants.Map.TILE / (corrected + 1))))
        scaled.set_alpha(shade)

        # 공격 시 붉은 틴트
        if self.state == constants.Enemy.STATE_ATTACK:
            tint = scaled.copy()
            tint.fill((120, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            scaled.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        col0 = cx - sprite_w // 2
        col1 = col0 + sprite_w
        
        y_bottom = hy + int(constants.Camera.PROJ_DIST * constants.Map.TILE * 0.5 / corrected)
        y_top    = y_bottom - sprite_h

        # 컬럼별 blit (z-buffer 체크)
        for col in range(max(0, col0), min(NR, col1)):
            if col < len(z_buffer) and z_buffer[col] < corrected: continue
            
            sprite_col = col - col0
            # 1px 슬라이스 추출 후 blit
            buf.blit(scaled, (col, y_top), pygame.Rect(sprite_col, 0, 1, sprite_h))

        # 체력 바
        if not self.is_dead and self.los and dist < self.sight_dist * 0.6:
            self._draw_hp_bar(buf, cx, y_top, sprite_w)


    def _draw_hp_bar(self, buf, cx, y_top, sprite_w):
        bar_w = max(12, sprite_w)
        bar_h = 4
        bar_x = cx - bar_w // 2
        bar_y = y_top - bar_h - 3
        ratio = self.cur_hp / self.max_hp

        pygame.draw.rect(buf, (80, 0, 0),   (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(buf, (0, 210, 0),  (bar_x, bar_y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(buf, (150,150,150),(bar_x, bar_y, bar_w, bar_h), 1)

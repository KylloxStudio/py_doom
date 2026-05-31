from __future__ import annotations
from typing import TYPE_CHECKING

import math
import pygame
import constants
from gun import Gun

if TYPE_CHECKING:
    from enemy import Enemy
    

class Player:
    def __init__(self):
        self.x     = 1.5 * constants.Map.TILE
        self.y     = 1.5 * constants.Map.TILE
        self.z     = 0.0    # 높이 (0=지면, + 위 / – 아래)
        self.vz    = 0.0    # 수직 속도
        self.angle = 0.0
        
        self.on_ground = True
        
        self.cur_hp = constants.Player.MAX_HP
        self.max_hp = constants.Player.MAX_HP
        
        self.potion = constants.Player.POTION_COUNT
        
        self.move_speed = constants.Player.MOVE_SPEED
        self.is_moving  = False
        
        self.is_jumping = False
        
        self._slide_timer = 0.0
        self._slide_dx    = 0.0
        self._slide_dy    = 0.0
        self.is_sliding   = False
        
        self.hit_timer  = 0.0
        self.kill_timer = 0.0
        
        self.gun = Gun(self)


    def jump(self):
        if self.on_ground and not self.is_sliding:
            self.vz = constants.Player.JUMP_VELOCITY
            self.is_jumping = True
            self.on_ground = False


    def get_slide_direction(self, keys):
        sa, ca = math.sin(self.angle), math.cos(self.angle)
        dx = dy = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dx += ca; dy += sa
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dx -= ca; dy -= sa
        if keys[pygame.K_a]:                         dx += sa; dy -= ca
        if keys[pygame.K_d]:                         dx -= sa; dy += ca
        length = math.hypot(dx, dy)
        if length > 0:
            return dx/length, dy/length
        
        return ca, sa

    def start_slide(self, nx, ny):
        """nx, ny: 정규화된 이동 방향."""
        if self.on_ground and not self.is_sliding:
            self.is_sliding  = True
            self._slide_timer = constants.Player.SLIDE_DURATION
            speed = self.move_speed * constants.Player.SLIDE_SPEED
            self._slide_dx = nx * speed
            self._slide_dy = ny * speed


    @property
    def cam_z(self):
        """점프 높이 + 슬라이딩 카메라 하강을 합산."""
        base = self.z * 1.5   # 점프로 인한 높이
        if self.is_sliding:
            # 슬라이딩 시작 시 급격히 내려갔다가 끝날 때 서서히 회복
            t = self._slide_timer / constants.Player.SLIDE_DURATION
            crouch = constants.Camera.OFFSET_Y_SLIDING * math.sin(t * math.pi)
            return base + crouch
        return base
    
    
    def update(self, events: list[pygame.event.Event], dt):
        from game import Game
        
        self.angle = Game.get().camera.yaw
        
        self.gun.update(events, dt)
        
        if not self.is_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.use_potion()
                    
                    if event.key == pygame.K_SPACE:
                        self.jump()

                    if event.key == pygame.K_LSHIFT:
                        keys_now = pygame.key.get_pressed()
                        nx, ny   = self.get_slide_direction(keys_now)
                        self.start_slide(nx, ny)
                        
            self.move(dt)

    
    def on_paused(self):
        self.is_moving  = False
        self.is_sliding = False
        
        
    def use_potion(self):
        if self.potion <= 0:
            return
        
        self.cur_hp += constants.Player.POTION_HEAL_AMOUNT
        self.potion -= 1
        
        from sound import Sound
        Sound.play(constants.Sound.POTION_PATH, constants.Sound.POTION_VOLUME)
        
        
    def killed_enemy(self, enemy: Enemy):
        from game import Game
        from sound import Sound
        
        Game.get().score += 100
        self.kill_timer = constants.Player.KILL_TIME
        
        Sound.play(constants.Sound.KILL_PATH, constants.Sound.KILL_VOLUME)
        
    
    @property
    def on_killed(self):
        return self.kill_timer > 0
    
    
    def take_damage(self, dmg: int):
        if self.is_hit or self.is_dead:
            return
        
        self.cur_hp -= dmg
        self.hit_timer  = 1.0
        
        if self.cur_hp <= 0:
            self.death()
            
        from sound import Sound
        Sound.play(constants.Sound.HIT_PATH, constants.Sound.HIT_VOLUME)
            
            
    @property
    def is_hit(self):
        return self.hit_timer >= 0
    
    
    def death(self):
        from game import Game
        
        self.cur_hp = 0
        
        self.is_moving  = False
        self.is_sliding = False
        
        self.gun.is_shooting  = False
        self.gun.is_reloading = False
        
        Game.get().state.gameover()
        
    
    @property
    def is_dead(self):
        return self.cur_hp <= 0
    
    
    def revive(self):
        self.x     = 1.5 * constants.Map.TILE
        self.y     = 1.5 * constants.Map.TILE
        self.z     = 0.0
        self.vz    = 0.0
        self.angle = 0.0
        
        self.cur_hp = self.max_hp
    
    
    def move(self, dt):
        from game import Game
        
        if self.is_hit:
            self.hit_timer -= dt * constants.Player.HIT_TIME_FACTOR
            
        if self.on_killed:
            self.kill_timer -= dt
        
        sa, ca = math.sin(self.angle), math.cos(self.angle)
        speed  = self.move_speed * dt * constants.Game.FRAME_RATE
        
        keys = pygame.key.get_pressed()

        if self.is_sliding:
            self.is_moving = True
            self._slide_timer -= dt
            t = max(0.0, self._slide_timer / constants.Player.SLIDE_DURATION)
            dx = self._slide_dx * dt * constants.Game.FRAME_RATE * (t ** (constants.Game.FRAME_RATE * 0.01))
            dy = self._slide_dy * dt * constants.Game.FRAME_RATE * (t ** (constants.Game.FRAME_RATE * 0.01))
            if self._slide_timer <= 0:
                self.is_moving = False
                self.is_sliding = False
        else:
            self.is_moving = any(keys[k] for k in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT))
            
            dx = 0
            dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dx += ca * speed;  dy += sa * speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dx -= ca * speed;  dy -= sa * speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx += sa * speed;  dy -= ca * speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx -= sa * speed;  dy += ca * speed

        self.angle %= 2 * math.pi

        # ─ 충돌 검사 후 이동 ─
        map = Game.get().map
        margin = 18
        
        if dx and not map.is_wall(self.x + dx + math.copysign(margin, dx), self.y):
            self.x += dx
        if dy and not map.is_wall(self.x, self.y + dy + math.copysign(margin, dy)):
            self.y += dy

        # ─ 점프 물리 (중력) ─
        if not self.on_ground:
            self.vz -= constants.Player.GRAVITY * dt
            
        self.z += self.vz * dt
        
        if self.z <= 0:
            self.z = 0.0
            self.vz = 0.0
            self.on_ground = True
            if self.is_jumping: self.is_jumping = False

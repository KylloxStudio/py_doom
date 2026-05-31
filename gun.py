from __future__ import annotations
from typing import TYPE_CHECKING

import math
import random
import pygame
import constants

if TYPE_CHECKING:
    from player import Player


class Gun:
    def __init__(self, owner: Player):
        self._owner = owner
        
        self.cur_ammo = 50
        self.max_ammo = 50
        
        self.shoot_damage_min = constants.Gun.SHOOT_DAMAGE_MIN
        self.shoot_damage_max = constants.Gun.SHOOT_DAMAGE_MAX
        self.shoot_cool       = constants.Gun.SHOOT_COOL
        self._shoot_timer     = 0.0
        self.is_shooting      = False
        
        self.reload_time   = constants.Gun.RELOAD_TIME
        self._reload_timer = 0.0
        self.is_reloading  = False
        
        self._bob        = 0.0
        self._cur_recoil = 0.0
        
    
    @property
    def shoot_damage(self):
        return random.randint(self.shoot_damage_min, self.shoot_damage_max)
        
        
    def update(self, events: list[pygame.event.Event], dt):
        if not self._owner.is_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.start_reload()

            mouse = pygame.mouse.get_pressed(5)
            self.is_shooting = mouse[0] and not self.is_reloading
            
            if self._cur_recoil > 0:
                self._cur_recoil = max(self._cur_recoil - 1.0, 0)
            
            if self.is_shooting:
                self._shoot_timer -= dt
                if self._shoot_timer <= 0:
                    self.shoot()
                    self._shoot_timer = self.shoot_cool
            else:
                if self.cur_ammo <= 0 and not self.is_reloading:
                    self.start_reload()
                
            if self.is_reloading:
                self._reload_timer -= dt
                if self._reload_timer <= 0:
                    self.reload()
    
    
    def on_paused(self):
        self.is_shooting  = False
        self.is_reloading = False
        
    
    def _check_hit(self):
        from game import Game
        
        px, py   = self._owner.x, self._owner.y
        angle    = self._owner.angle
        cos_a    = math.cos(angle)
        sin_a    = math.sin(angle)

        for enemy in Game.get().enemies:
            if enemy.is_dead or not enemy.los:
                continue
            
            dx   = enemy.x - px
            dy   = enemy.y - py
            dist = math.hypot(dx, dy)
            
            if dist < 1:
                continue
            
            # 적이 조준선(시야 중앙) 근처에 있는지 확인
            dot   = (dx * cos_a + dy * sin_a) / dist                                                # 코사인 유사도
            cross = abs(dx * sin_a - dy * cos_a)                                                    # 수직 거리
            hit_w = constants.Map.TILE * 0.8 * (constants.Map.TILE / max(dist, constants.Map.TILE)) # 거리 비례 판정 너비 (멀수록 좁아짐)

            if dot > 0.95 and cross < hit_w:
                Game.get().score += self.shoot_damage
                enemy.take_damage(self._owner, self.shoot_damage)
                break


    def shoot(self):
        if self.cur_ammo <= 0:
            return
        
        from game import Game
        from sound import Sound
        
        self._check_hit()
        
        self._cur_recoil += constants.Gun.SHOOT_RECOIL_AMOUNT
        self.cur_ammo -= 1
        
        camera = Game.get().camera
        
        camera.add_yaw((random.random() - self._cur_recoil * 0.1) * 0.01)
        camera.add_pitch(-self._cur_recoil * 2.5)
        
        Sound.play(constants.Sound.SHOOT_PATH, constants.Sound.SHOOT_VOLUME)
            
    
    def start_reload(self):
        if self.is_reloading or self.cur_ammo >= self.max_ammo:
            return
        
        self._reload_timer = self.reload_time
        self.is_reloading = True
        
        from sound import Sound
        Sound.play(constants.Sound.RELOAD_PATH, constants.Sound.RELOAD_VOLUME)
            
    
    def reload(self):
        self.cur_ammo = self.max_ammo
        self.is_reloading = False
    

    # 렌더링
    def draw(self, screen: pygame.Surface):
        self._update_bob()
        self._draw_3d(screen, self._cur_recoil / constants.Gun.SHOOT_RECOIL_AMOUNT if self._cur_recoil > 0 else 0.0)


    def _update_bob(self):
        moving = self._owner.is_moving and not self._owner.is_sliding
        if moving:
            self._bob += 0.15
        else:
            self._bob *= 0.8


    def _draw_3d(self, screen: pygame.Surface, recoil: float):
        SW = constants.Game.SCREEN_WIDTH
        SH = constants.Game.SCREEN_HEIGHT

        # ── 흔들림 / 점프 / 슬라이딩 오프셋 ─────────────────────────
        bob_y = math.sin(self._bob) * 0.018
        bob_x = math.cos(self._bob * 0.5) * 0.009

        extra_y = 0.0
        if self._owner.is_sliding:
            t = self._owner._slide_timer / constants.Player.SLIDE_DURATION
            extra_y = math.sin(t * math.pi) * 0.07
        elif not self._owner.on_ground:
            extra_y = -self._owner.z * 0.00035

        # ── 카메라 공간 내 총 위치 ────────────────────────────────────
        GX =  0.32 + bob_x
        GY = -0.18 + bob_y + extra_y + recoil * 0.07
        GZ =  0.75 - recoil * 0.14

        PITCH = -0.10   # 총구 약간 아래
        YAW   = -0.06   # 총구 약간 좌측 (화면 중앙 방향)

        cp, sp   = math.cos(PITCH), math.sin(PITCH)
        cyw, syw = math.cos(YAW),   math.sin(YAW)

        def transform(x, y, z):
            """로컬 좌표 → 카메라 공간"""
            x2 = x * cyw + z * syw
            z2 = -x * syw + z * cyw
            y3 = y * cp  - z2 * sp
            z3 = y * sp  + z2 * cp
            return x2 + GX, y3 + GY, z3 + GZ

        def rot_n(nx, ny, nz):
            """법선 벡터만 회전 (이동 없음)"""
            x2 = nx * cyw + nz * syw
            z2 = -nx * syw + nz * cyw
            y3 = ny * cp  - z2 * sp
            z3 = ny * sp  + z2 * cp
            return x2, y3, z3

        # ── 원근 투영 ─────────────────────────────────────────────────
        FOCAL = 720
        def proj(x, y, z):
            z = max(z, 0.001)
            return (
                int(SW // 2 + x / z * FOCAL),
                int(SH // 2 - y / z * FOCAL + SH * 0.22),
            )

        def tp(x, y, z):
            return proj(*transform(x, y, z))

        # ── 조명 ──────────────────────────────────────────────────────
        LX, LY, LZ = -0.3, 0.8, -0.4
        lm = math.sqrt(LX**2 + LY**2 + LZ**2)
        LX, LY, LZ = LX / lm, LY / lm, LZ / lm

        def lit(nx, ny, nz, base):
            rnx, rny, rnz = rot_n(nx, ny, nz)
            d = max(0.15, rnx * LX + rny * LY + rnz * LZ)
            f = 0.25 + d
            return tuple(min(255, int(c * f)) for c in base)

        # ── 박스 → 면 버퍼 ────────────────────────────────────────────
        buf = []  # (depth, pts2d, color)

        def add_box(x1, x2, y1, y2, z1, z2, base):
            """박스의 보이는 면을 버퍼에 추가 (백페이스 컬링 적용)"""
            faces = [
                ((0,  0, -1), [(x1,y1,z1),(x2,y1,z1),(x2,y2,z1),(x1,y2,z1)]),  # 뒷면(카메라쪽)
                ((0,  0,  1), [(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)]),  # 앞면(총구쪽)
                ((0,  1,  0), [(x1,y2,z1),(x2,y2,z1),(x2,y2,z2),(x1,y2,z2)]),  # 윗면
                ((0, -1,  0), [(x1,y1,z1),(x2,y1,z1),(x2,y1,z2),(x1,y1,z2)]),  # 아랫면
                ((-1, 0,  0), [(x1,y1,z1),(x1,y2,z1),(x1,y2,z2),(x1,y1,z2)]),  # 왼쪽면
                (( 1, 0,  0), [(x2,y1,z1),(x2,y2,z1),(x2,y2,z2),(x2,y1,z2)]),  # 오른쪽면
            ]
            for normal, verts in faces:
                # 면 중심을 카메라 공간으로 변환
                tcx, tcy, tcz = transform(
                    sum(v[0] for v in verts) / 4,
                    sum(v[1] for v in verts) / 4,
                    sum(v[2] for v in verts) / 4,
                )
                # 백페이스 컬링: 법선·시선 내적 < 0 이면 카메라를 향하는 면
                rnx, rny, rnz = rot_n(*normal)
                if rnx * tcx + rny * tcy + rnz * tcz < 0:
                    tv    = [transform(*v) for v in verts]
                    depth = sum(v[2] for v in tv) / 4
                    buf.append((depth, [proj(*v) for v in tv], lit(*normal, base)))

        # ── 총 형태 ───────────────────────────────────────────────────
        # 좌표계: x=좌우, y=상하, z=총구 방향(+Z=앞)
        B = (50, 52, 65)  # 기본 바디 색

        add_box(-0.11,  0.11,  -0.09,  0.09,   0.00,  0.45, B)               # 리시버
        add_box(-0.065, 0.065, -0.055, 0.055,  0.45,  1.40, (36, 38, 50))    # 배럴
        add_box(-0.09,  0.09,  -0.32, -0.09,   0.08,  0.30, B)               # 그립
        add_box(-0.10,  0.10,  -0.08,  0.08,  -0.22,  0.00, (44, 46, 58))    # 스톡
        add_box(-0.055, 0.055, -0.22, -0.09,   0.10,  0.27, (40, 42, 54))    # 매거진

        # ── 페인터 알고리즘 (먼 면 → 가까운 면 순) ───────────────────
        buf.sort(key=lambda f: -f[0])

        OL = (18, 18, 28)
        for _, pts, color in buf:
            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, OL,    pts, 1)

        # ── 총구 화염 ─────────────────────────────────────────────────
        if recoil > 0:
            rv     = recoil
            mx, my = tp(0, 0, 1.45)
            outer  = [
                (mx,    my),
                (mx-15, my-18), (mx-5,  my-13),
                (mx-22, my-36), (mx-2,  my-24),
                (mx-13, my-50), (mx+5,  my-27),
                (mx+12, my-20), (mx+10, my),
            ]
            inner  = [
                (mx,   my-2),  (mx-5,  my-12),
                (mx-1, my-10), (mx-9,  my-26),
                (mx+2, my-16), (mx-3,  my-32),
                (mx+5, my-17), (mx+7,  my-2),
            ]
            
            def cc(v):  # 색상값 클램핑
                return max(0, min(255, int(v)))
            
            pygame.draw.polygon(screen, (cc(255), cc(145 * rv), 0), outer)
            pygame.draw.polygon(screen, (cc(255), cc(238), cc(80 * rv)), inner)

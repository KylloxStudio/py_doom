from __future__ import annotations
from typing import TYPE_CHECKING
    
import math
import pygame
import constants

if TYPE_CHECKING:
    from map import Map
    from player import Player
    from enemy import Enemy


class UI:
    def __init__(self):
        from font import Font
        
        self._font_m = Font.load_font(constants.UI.MAIN_FONT_PATH, constants.UI.FONT_SIZE_M, bold=True)
        self._font_s = Font.load_font(constants.UI.MAIN_FONT_PATH, constants.UI.FONT_SIZE_S)
    
    
    def draw_minimap(self, screen: pygame.Surface, player: Player, map: Map, enemies: list[Enemy]):
        MS, OX, OY = 7, 10, 10

        # 배경
        bg_w = map.width  * MS + 2
        bg_h = map.height * MS + 2
        pygame.draw.rect(screen, (40, 40, 40), (OX - 1, OY - 1, bg_w, bg_h))

        # 맵
        for ry in range(map.height):
            for rx in range(map.width):
                c = (90,90,90) if map.data[ry][rx] == "1" else (30,30,30)
                pygame.draw.rect(screen, c, (OX+rx*MS, OY+ry*MS, MS-1, MS-1))

        # 적 위치
        if enemies:
            for enemy in enemies:
                ex = int(OX + enemy.x / constants.Map.TILE * MS)
                ey = int(OY + enemy.y / constants.Map.TILE * MS)
                
                if enemy.is_dead:
                    pygame.draw.circle(screen, (60, 60, 60), (ex, ey), 2)
                    
                elif enemy.los:
                    pygame.draw.circle(screen, (220, 40, 40), (ex, ey), 3)  # 시야 내
                    
                else:
                    pygame.draw.circle(screen, (140, 60, 60), (ex, ey), 2)  # 벽 뒤

        # 플레이어
        px = int(OX + player.x / constants.Map.TILE * MS)
        py = int(OY + player.y / constants.Map.TILE * MS)
        
        pygame.draw.circle(screen, constants.Color.GREEN, (px, py), 3)
        pygame.draw.line(screen, constants.Color.GREEN, (px, py), (int(px + math.cos(player.angle) * 9), int(py + math.sin(player.angle) * 9)), 2)


    def draw_crosshair(self, screen: pygame.Surface):
        cx, cy = constants.Game.SCREEN_WIDTH//2, constants.Game.SCREEN_HEIGHT//2
        pygame.draw.line(screen, constants.Color.WHITE, (cx-10,cy), (cx+10,cy), 2)
        pygame.draw.line(screen, constants.Color.WHITE, (cx,cy-10), (cx,cy+10), 2)
        
        
    def draw_hud(self, screen: pygame.Surface, player: Player, fps: float, score: int):
        hud = pygame.Surface((constants.Game.SCREEN_WIDTH, 44), pygame.SRCALPHA)
        hud.fill((0,0,0,160))
        screen.blit(hud, (0, constants.Game.SCREEN_HEIGHT-44))

        hp_color = (0,220,0) if player.cur_hp>60 else (220,80,0) if player.cur_hp>30 else (220,0,0)
        screen.blit(self._font_m.render(f"{player.cur_hp}%", True, hp_color), (20, constants.Game.SCREEN_HEIGHT-36))
        
        potion_color = (0,180,0) if player.potion>=3 else (180,60,0) if player.potion>=2 else (180,20,20) if player.potion>=1 else (200,0,0)
        screen.blit(self._font_m.render(f"{player.potion} / {constants.Player.POTION_COUNT}", True, potion_color), (120, constants.Game.SCREEN_HEIGHT-36))
        
        surf_ammo = self._font_m.render(f"{player.gun.cur_ammo} / {player.gun.max_ammo}", True, (180,180,180))
        screen.blit(surf_ammo, (constants.Game.SCREEN_WIDTH-20 - surf_ammo.get_width(), constants.Game.SCREEN_HEIGHT-36))
        
        surf_fps = self._font_s.render(f"FPS {int(fps):02d}", True, (180,180,180))
        screen.blit(surf_fps, (constants.Game.SCREEN_WIDTH-20 - surf_fps.get_width(), 15))
        
        surf_score = self._font_s.render(f"SCORE: {score}", True, (32, 128, 32))
        screen.blit(surf_score, (constants.Game.SCREEN_WIDTH-20 - surf_score.get_width(), 30))

        # hint = "WASD: 이동  마우스 이동: 회전  SPACE: 점프  LCTRL: 슬라이딩  좌클릭: 사격  ESC: 종료"
        # htxt = self._font_s.render(hint, True, (160,160,160))
        # screen.blit(htxt, (constants.Game.SCREEN_WIDTH//2 - htxt.get_width()//2, constants.Game.SCREEN_HEIGHT-36))
        
        
    def draw_player_state(self, screen: pygame.Surface, player: Player):
        def get_overlay_alpha(n):
            if n > 60:
                t = (n - 60) / 40   # 100→60 구간: 0→0 (고정)
                return 0
            elif n > 30:
                t = (n - 30) / 30          # 60→30 구간: 0~1
                return int(75 * (1 - t))   # 75→0
            else:
                t = n / 30                     # 30→0 구간: 0~1
                return int(75 + 75 * (1 - t))  # 75→150
    
        SW = constants.Game.SCREEN_WIDTH
        SH = constants.Game.SCREEN_HEIGHT

        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        
        alpha = get_overlay_alpha(player.cur_hp)
        overlay.fill((150, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        
        label_f = ""
        color_f = (200, 200, 200)
        
        label_s = ""
        color_s = (200, 200, 200)
        
        if player.is_sliding:
            label_f = "→ SLIDING"
            color_f = (100, 220, 255)
        
        if player.is_jumping:
            label_f = "↑ JUMPING"
            color_f = (255, 220, 80)
            
        if player.on_killed:
            label_s = "ENEMY ELIMINATED: +100"
            color_s = (160, 32, 32)
        
        if label_f:
            txt = self._font_s.render(label_f, True, color_f)
            screen.blit(txt, (SW//2 - txt.get_width()//2, SH//2 - 50))
        
        if label_s:
            txt = self._font_s.render(label_s, True, color_s)
            screen.blit(txt, (SW//2 - txt.get_width()//2, SH//2 + 50))
    
    
    def draw_hit_flash(self, screen: pygame.Surface, player: Player):
        if player.hit_timer <= 0:
            return
        
        SW = constants.Game.SCREEN_WIDTH
        SH = constants.Game.SCREEN_HEIGHT

        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        
        alpha = int(player.hit_timer * 80)
        overlay.fill((150, 0, 0, alpha))

        # 화면 테두리만 붉게 (비네팅 효과)
        # alpha   = int(player.hit_flash * 180)
        # border  = int(player.hit_flash)
        # overlay.fill((0, 0, 0, 0))
        
        # pygame.draw.rect(overlay, (200, 0, 0, alpha), (0, 0, SW, border))
        # pygame.draw.rect(overlay, (200, 0, 0, alpha), (0, SH-border, SW, border))
        # pygame.draw.rect(overlay, (200, 0, 0, alpha), (0, 0, border, SH))
        # pygame.draw.rect(overlay, (200, 0, 0, alpha), (SW-border, 0, border, SH))
        
        screen.blit(overlay, (0, 0))

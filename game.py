import os
import math
import ctypes
import pygame
import constants
from ui import UI
from map import Map
from font import Font
from sound import Sound
from enemy import Enemy
from camera import Camera
from player import Player
from state import State
from resources import Resources

class Game:
    _instance = None

    @classmethod
    def get(cls):
        return cls._instance
    
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PyDOOM")
        
        icon = pygame.image.load(Resources.get_path('icon.png'))
        pygame.display.set_icon(icon)

        info = pygame.display.Info()
        self._monitor_w = info.current_w
        self._monitor_h = info.current_h
        
        self.screen         = pygame.display.set_mode((constants.Game.WINDOW_WIDTH, constants.Game.WINDOW_HEIGHT))
        self.render_surface = pygame.Surface((constants.Game.SCREEN_WIDTH, constants.Game.SCREEN_HEIGHT))
        self.buffer         = pygame.Surface((constants.Camera.NUM_RAYS, constants.Game.SCREEN_HEIGHT))
        
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.clock = pygame.time.Clock()
        
        self.sound   = Sound()
        self.ui      = UI()
        self.map     = Map()
        self.font    = Font()
        self.camera  = Camera()
        self.player  = Player()
        self.enemies = self.get_enemies()
        self.state   = State()

        self.is_fullscreen = False

        self.score = 0
        self.score_timer = constants.Game.SCORE_TIME
        self.is_running = False
        self.is_paused = False
        
        Game._instance = self
        
        
    def _center_window(self):
        hwnd = pygame.display.get_wm_info()['window']
        x = (self._monitor_w - constants.Game.WINDOW_WIDTH)  // 2
        y = (self._monitor_h - constants.Game.WINDOW_HEIGHT) // 2
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001)
        
        
    def _center_full(self):
        hwnd = pygame.display.get_wm_info()['window']
        x = (self._monitor_w - constants.Game.WINDOW_WIDTH)  // 2
        y = (self._monitor_h - constants.Game.WINDOW_HEIGHT) // 2
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001)
        
        
    def toggle_fullscreen(self):
        hwnd = pygame.display.get_wm_info()['window']
        
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((constants.Game.WINDOW_WIDTH, constants.Game.WINDOW_HEIGHT))
            self.is_fullscreen = False
            x = (self._monitor_w - constants.Game.WINDOW_WIDTH)  // 2
            y = (self._monitor_h - constants.Game.WINDOW_HEIGHT) // 2
        else:
            self.screen = pygame.display.set_mode((self._monitor_w, self._monitor_h), pygame.NOFRAME)
            self.is_fullscreen = True
            x = 0
            y = 0
        
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001)
        
    
    def _blit_to_screen(self):
        """render_surface를 화면 비율에 맞게 스케일해서 출력."""
        
        sw, sh = self.screen.get_size()
        rw, rh = self.render_surface.get_size()

        # 비율 유지 스케일
        scale = min(sw / rw, sh / rh)
        new_w = int(rw * scale)
        new_h = int(rh * scale)

        scaled = pygame.transform.scale(self.render_surface, (new_w, new_h))

        # 가운데 정렬
        x = (sw - new_w) // 2
        y = (sh - new_h) // 2

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (x, y))
        
    
    def draw_ingame(self):
        hy = self.camera.horizon_y(self.player)
        self.draw_background(hy)
        self.map.draw_walls(self.buffer, self.player, hy)

        self.enemies.sort(key=lambda e: math.hypot(e.x - self.player.x, e.y - self.player.y), reverse=True)
        for enemy in self.enemies:
            enemy.draw(self.buffer, self.player, self.map.z_buffer, hy)

        scaled_buf = pygame.transform.scale(self.buffer, (constants.Game.SCREEN_WIDTH, constants.Game.SCREEN_HEIGHT))
        self.render_surface.blit(scaled_buf, (0, 0))

        self.player.gun.draw(self.render_surface)
        self.ui.draw_minimap(self.render_surface, self.player, self.map, self.enemies)
        self.ui.draw_crosshair(self.render_surface)
        self.ui.draw_hit_flash(self.render_surface, self.player)
        self.ui.draw_player_state(self.render_surface, self.player)
        self.ui.draw_hud(self.render_surface, self.player, self.clock.get_fps(), self.score)

        pygame.transform.scale(self.render_surface, self.screen.get_size(), self.screen)
        
        
    def draw_background(self, hy):
        self.buffer.fill(constants.Color.CEILING, (0,  0,  constants.Camera.NUM_RAYS, hy))
        self.buffer.fill(constants.Color.FLOOR, (0,  hy, constants.Camera.NUM_RAYS, constants.Game.SCREEN_HEIGHT - hy))
        
    
    def get_enemies(self):
        T = constants.Map.TILE
        return [Enemy(x * T, y * T) for x, y in constants.Map.ENEMIES_SPAWN_POS]
    
    
    def start_game(self):
        self.is_paused = False
        self.score = 0
        
        self.player = Player()
        self.enemies = self.get_enemies()
        
        self.state.start()
    
    
    def pause_game(self):
        self.is_paused = True
        self.state.pause()
    
    
    def un_pause_game(self):
        self.is_paused = False
        self.state.resume()


    # 메인 루프
    def run(self):
        self.is_running = True
        while self.is_running:
            raw_dt = self.clock.tick(constants.Game.FRAME_RATE) / 1000.0
            dt = 0.0 if self.is_paused else min(raw_dt, 0.05)
            
            # if self.score_timer <= 0:
            #     self.score += 1
            #     self.score_timer = constants.Game.SCORE_TIME
            # else:
            #     self.score_timer -= dt

            events = pygame.event.get();
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
        
                if event.type == pygame.QUIT:
                    self.is_running = False

                action = self.state.handle_event(event)
                if action == "start":
                    self.start_game()
                    
                elif action == "pause":
                    self.pause_game()
                    
                elif action == "resume":
                    self.un_pause_game()
                    
                elif action == "main":
                    self.state.to_main()
                    
                elif action == "quit":
                    self.is_running = False

            if self.state.is_ingame:
                self.camera.update(events)
                self.player.update(events, dt)
                
                if not any(not e.is_dead for e in self.enemies):
                    self.enemies = self.get_enemies()
            
                for enemy in self.enemies:
                    enemy.update(self.player, dt)
            
            if self.state.is_ingame or self.state.is_paused or self.state.is_gameover:
                self.draw_ingame()
            
            self.state.draw(self.render_surface, raw_dt)
            
            self._blit_to_screen()
            pygame.display.flip()
    
        pygame.quit()

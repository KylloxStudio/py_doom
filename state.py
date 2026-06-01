import pygame
import math
import constants


class State:
    def __init__(self):
        from font import Font
        
        self.current  = constants.State.MAIN
        self._tick    = 0.0   # 애니메이션용 타이머

        self._main_items   = ["GAME START", "QUIT"]
        self._main_sel     = 0
        
        self._pause_items  = ["RESUME", "MAIN MENU", "QUIT"]
        self._pause_sel    = 0
        
        self._gameover_items  = ["RESTART", "MAIN MENU", "QUIT"]
        self._gameover_sel    = 0

        self._font_xxl = Font.load_font(constants.UI.MAIN_FONT_PATH, constants.UI.FONT_SIZE_XXL, bold=True)
        self._font_l  = Font.load_font(constants.UI.MAIN_FONT_PATH, constants.UI.FONT_SIZE_L, bold=True)
        self._font_m  = Font.load_font(constants.UI.MAIN_FONT_PATH, constants.UI.FONT_SIZE_M)
        self._font_s  = Font.load_font(constants.UI.MAIN_FONT_PATH, constants.UI.FONT_SIZE_S)
    

    # ── 상태 확인 ────────────────────────────────────────────────────
    @property
    def is_main(self):
        return self.current == constants.State.MAIN
    
    @property
    def is_ingame(self):
        return self.current == constants.State.INGAME
    
    @property
    def is_paused(self):
        return self.current == constants.State.PAUSED
    
    @property
    def is_gameover(self):
        return self.current == constants.State.GAMEOVER


    def start(self):
        self.current = constants.State.INGAME
      
    
    def pause(self):
        from game import Game
        
        Game.get().player.on_paused()
        Game.get().player.gun.on_paused()
        
        self.current = constants.State.PAUSED
        self._pause_sel = 0
      
    
    def resume(self):
        self.current = constants.State.INGAME
        
    
    def gameover(self):
        self.current = constants.State.GAMEOVER
        self._gameover_sel = 0
      
    
    def to_main(self):
        self.current = constants.State.MAIN
        self._main_sel = 0


    def handle_event(self, event: pygame.event.Event, is_web):
        pause_key = pygame.K_p if is_web else pygame.K_ESCAPE
        
        if event.type == pygame.KEYDOWN:
            if self.is_main:
                if event.key == pygame.K_UP:
                    self._main_sel = (self._main_sel - 1) % len(self._main_items)
                    
                elif event.key == pygame.K_DOWN:
                    self._main_sel = (self._main_sel + 1) % len(self._main_items)
                    
                elif event.key == pygame.K_RETURN:
                    return ["start", "quit"][self._main_sel]

            elif self.is_ingame:
                if event.key == pause_key:
                    return "pause"

            elif self.is_paused:
                if event.key == pygame.K_UP:
                    self._pause_sel = (self._pause_sel - 1) % len(self._pause_items)
                    
                elif event.key == pygame.K_DOWN:
                    self._pause_sel = (self._pause_sel + 1) % len(self._pause_items)
                    
                elif event.key == pygame.K_RETURN:
                    return ["resume", "main", "quit"][self._pause_sel]
                
                elif event.key == pause_key:
                    return "resume"
            
            elif self.is_gameover:
                if event.key == pygame.K_UP:
                    self._gameover_sel = (self._gameover_sel - 1) % len(self._gameover_items)
                    
                elif event.key == pygame.K_DOWN:
                    self._gameover_sel = (self._gameover_sel + 1) % len(self._gameover_items)
                    
                elif event.key == pygame.K_RETURN:
                    return ["start", "main", "quit"][self._gameover_sel]

        return None


    def draw(self, screen: pygame.Surface, dt: float):
        self._tick += dt
        
        if self.is_main:
            self._draw_main(screen)
            
        elif self.is_paused:
            self._draw_paused(screen)
        
        elif self.is_gameover:
            self._draw_gameover(screen)


    def _draw_main(self, screen: pygame.Surface):
        SW = constants.Game.SCREEN_WIDTH
        SH = constants.Game.SCREEN_HEIGHT

        # 배경
        screen.fill((8, 8, 12))
        self._draw_grid(screen, SW, SH)

        # 제목
        pulse = 0.08 * math.sin(self._tick * 2.5)
        title_color = (
            min(255, int(220 + pulse * 255)),
            min(255, int(30  + pulse * 60)),
            min(255, int(30  + pulse * 60)),
        )
        
        self._draw_text_centered(screen, "PyDOOM", self._font_xxl, title_color, SH // 2 - 160)
        self._draw_text_centered(screen, "Made by JJM", self._font_s, (120, 120, 140), SH // 2 - 80)

        # 구분선
        line_y = SH // 2 - 55
        pygame.draw.line(screen, (60, 20, 20), (SW // 2 - 200, line_y), (SW // 2 + 200, line_y), 1)

        # 메뉴 아이템
        for i, item in enumerate(self._main_items):
            y = SH // 2 + i * 60
            selected = (i == self._main_sel)
            self._draw_menu_item(screen, item, y, selected, SW)

        # 조작 안내
        self._draw_text_centered(screen, "↑↓ 선택   |   ENTER 확인", self._font_s, (60, 60, 80), SH - 40)


    def _draw_paused(self, screen: pygame.Surface):
        SW = constants.Game.SCREEN_WIDTH
        SH = constants.Game.SCREEN_HEIGHT

        # 반투명 오버레이 (게임 화면 위에 덮음)
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        # PAUSED 제목
        self._draw_text_centered(screen, "PAUSED", self._font_xxl, (0, 100, 180), SH // 2 - 150)

        # 메뉴 아이템
        for i, item in enumerate(self._pause_items):
            y = SH // 2 - 10 + i * 52
            selected = (i == self._pause_sel)
            self._draw_menu_item(screen, item, y, selected, SW)

        # 조작 안내
        self._draw_text_centered(screen, "↑↓ 선택   |   ENTER 확인   |   ESC 재개", self._font_s, (80, 80, 100), SH - 40)
        
    
    def _draw_gameover(self, screen: pygame.Surface):
        SW = constants.Game.SCREEN_WIDTH
        SH = constants.Game.SCREEN_HEIGHT
        
        BAND_Y = SH // 2 - 220
        BAND_H = 120
        
        # 반투명 오버레이 (게임 화면 위에 덮음)
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        band = pygame.Surface((SW, BAND_H), pygame.SRCALPHA)
        band.fill((15, 5, 5, 200))
        screen.blit(band, (0, BAND_Y))

        # 띠 상단/하단에 정확히 맞춤
        for y, alpha in [(BAND_Y, 180), (BAND_Y + BAND_H, 180)]:
            s = pygame.Surface((SW, 2), pygame.SRCALPHA)
            s.fill((180, 30, 30, alpha))
            screen.blit(s, (0, y))

        self._draw_text_centered(screen, "GAME OVER", self._font_xxl, (220, 40, 40), SH // 2 - 200)

        # 메뉴 아이템
        for i, item in enumerate(self._gameover_items):
            y = SH // 2 - 10 + i * 52
            selected = (i == self._gameover_sel)
            self._draw_menu_item(screen, item, y, selected, SW)

        # 조작 안내
        self._draw_text_centered(screen, "↑↓ 선택   |   ENTER 확인", self._font_s, (80, 80, 100), SH - 40)


    # ── 공통 유틸 ────────────────────────────────────────────────────
    def _draw_menu_item(self, screen, text, y, selected, SW):
        if selected:
            # 선택된 항목: 배경 바 + 화살표 + 밝은 글자
            bar = pygame.Surface((340, 44), pygame.SRCALPHA)
            bar.fill((180, 30, 30, 80))
            screen.blit(bar, (SW // 2 - 170, y - 4))
            pygame.draw.rect(screen, (180, 30, 30), (SW // 2 - 170, y - 4, 340, 44), 1)

            # 깜빡이는 화살표
            if int(self._tick * 2) % 2 == 0:
                arrow = self._font_l.render("▶", True, (220, 60, 60))
                screen.blit(arrow, (SW // 2 - 155, y))

            color = (255, 220, 220)
        else:
            color = (130, 130, 150)

        surf = self._font_l.render(text, True, color)
        screen.blit(surf, (SW // 2 - surf.get_width() // 2, y))


    def _draw_text_centered(self, screen, text, font, color, y):
        surf = font.render(text, True, color)
        screen.blit(surf, (constants.Game.SCREEN_WIDTH // 2 - surf.get_width() // 2, y))


    def _draw_grid(self, screen, SW, SH):
        """배경 격자 (원근감 있는 바닥 선)"""
        color = (22, 8, 8)
        # 수평선
        for i in range(1, 12):
            y = SH // 2 + i * 40
            if y < SH:
                pygame.draw.line(screen, color, (0, y), (SW, y), 1)
        # 수직선 (원근 수렴)
        vp_x = SW // 2
        vp_y = SH // 2
        for i in range(-12, 13):
            ex = vp_x + i * 80
            pygame.draw.line(screen, color, (vp_x, vp_y), (ex, SH), 1)
    
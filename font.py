import pygame
import constants


class Font:
    @staticmethod
    def load_font(path, size, bold=False, italic=False):
        try:
            font = pygame.font.Font(path, size)
            if bold:   font.set_bold(True)
            if italic: font.set_italic(italic)
            return font
        except FileNotFoundError:
            print("폰트 파일 못 찾음")
            return pygame.font.SysFont(constants.UI.DEFAULT_FONT_NAME, size, bold=bold, italic=italic)

import pygame


class Sound:
    def __init__(self):
        pygame.mixer.init()
  

    @staticmethod
    def play(path, volume=1.0):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        sound.play()
    
    
    @staticmethod
    def stop(path):
        sound = pygame.mixer.Sound(path)
        sound.stop()

import pygame
import asyncio
from game import *


async def main():
    pygame.init()
    
    game = Game()
    await game.run()

asyncio.run(main())

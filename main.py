import asyncio
from game import *

async def main():
    game = Game()
    game.run()

asyncio.run(main())

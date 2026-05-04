import asyncio
from game import GameState

async def main():
    gs = GameState()
    gs.add_player("p1", "Alice")
    print(gs.get_state())
    out = gs.tick(0.033)
    print(out)
    gs.start_game()
    print("Started game")
    out = gs.tick(0.033)
    print(out)

if __name__ == "__main__":
    asyncio.run(main())

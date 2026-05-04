import asyncio
from game import GameState

async def main():
    gs = GameState()
    gs.add_player("p1", "Alice")
    try:
        out = gs.tick(0.033)
        print("Tick 1 success")
        state = gs.get_state()
        print("State 1 success")
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())

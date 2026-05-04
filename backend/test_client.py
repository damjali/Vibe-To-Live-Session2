import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8001/ws?name=Test") as ws:
        init_msg = await ws.recv()
        print("Init:", init_msg)
        for i in range(5):
            state_msg = await ws.recv()
            print("State:", len(state_msg))
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(test())

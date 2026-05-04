import asyncio
import uuid
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from connection_manager import manager
from game import GameState

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_state = GameState()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, name: str = "Anonymous"):
    player_id = str(uuid.uuid4())
    await manager.connect(websocket, player_id)
    game_state.add_player(player_id, name)
    
    # Send init message
    await manager.send_personal_message(
        {
            "type": "init",
            "data": {
                "playerId": player_id,
                "arenaRadius": game_state.arenaRadius
            }
        },
        player_id
    )

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "input":
                target_x = data["data"]["x"]
                target_y = data["data"]["y"]
                game_state.set_player_target(player_id, target_x, target_y)
            elif data["type"] == "start_game":
                if game_state.admin_id == player_id:
                    game_state.start_game()
            elif data["type"] == "play_again":
                if game_state.admin_id == player_id:
                    game_state.reset_game()
    except WebSocketDisconnect:
        manager.disconnect(player_id)
        game_state.remove_player(player_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(player_id)
        game_state.remove_player(player_id)

async def game_loop():
    fps = 30
    dt = 1.0 / fps
    while True:
        await asyncio.sleep(dt)
        
        # Tick game
        out_of_bounds_players = game_state.tick(dt)
        
        # Handle out of bounds
        for p_id in out_of_bounds_players:
            await manager.send_personal_message(
                {
                    "type": "personal_game_over",
                    "data": {
                        "reason": "out_of_bounds",
                        "message": "You fell out! Spectating..."
                    }
                },
                p_id
            )

        # Broadcast state
        state_data = game_state.get_state()
        await manager.broadcast({
            "type": "state",
            "data": state_data
        })

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(game_loop())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

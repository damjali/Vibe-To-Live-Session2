import asyncio
import uuid
import uvicorn
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Serve static files from the "static" directory
# Change "static" to "frontend/dist" for local development
# Define possible locations for the frontend build using absolute paths
base_dir = os.path.dirname(os.path.abspath(__file__))
static_options = [
    os.path.join(base_dir, "static"),          # Docker location (backend/static)
    os.path.join(base_dir, "..", "frontend", "dist"), # Local development (parent/frontend/dist)
    os.path.join(base_dir, "frontend", "dist"), # Another common local layout
]

static_dir = None
for option in static_options:
    if os.path.exists(option):
        static_dir = option
        break

if static_dir:
    print(f"Serving static files from: {static_dir}")
    # Mount assets directory for efficient serving of JS/CSS/Images
    assets_path = os.path.join(static_dir, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    # Catch-all route to serve the SPA index.html for any unknown paths (for client-side routing)
    @app.get("/{full_path:path}")
    async def serve_static(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    print(f"CRITICAL: No static files directory found! Searched in: {static_options}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

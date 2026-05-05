import json
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: str):
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def send_personal_message(self, message: dict, player_id: str):
        if player_id in self.active_connections:
            try:
                await self.active_connections[player_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to {player_id}: {e}")

    async def broadcast(self, message: dict):
        # We need to collect disconnected players to remove them later
        disconnected_players = []
        for player_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to {player_id}: {e}")
                disconnected_players.append(player_id)
        
        for player_id in disconnected_players:
            self.disconnect(player_id)

manager = ConnectionManager()

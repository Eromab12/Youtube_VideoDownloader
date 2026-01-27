from typing import List
from fastapi import WebSocket

class LogManager:
    """
    Manages WebSocket connections for streaming logs.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # If sending fails, we might want to remove the connection, 
                # but let's leave it to the disconnect handler for now to avoid modifying list while iterating
                pass

log_manager = LogManager()

from app.svc.room import RoomService
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .routers import health, auth, websocket, debug

app = FastAPI(
    title="Chess CG API", description="A chess game backend API", version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared services
room_service = RoomService()

# Set up shared services in routers
websocket.room_service = room_service
debug.room_service = room_service

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(websocket.router)
app.include_router(debug.router)



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

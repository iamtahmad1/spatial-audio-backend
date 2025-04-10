from fastapi import FastAPI
from app.api.v1 import health, users, rooms, login
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Spatial Audio Backend")

app.include_router(health.router)
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(login.router, prefix="/auth", tags=["Auth"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:8001"] for more control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
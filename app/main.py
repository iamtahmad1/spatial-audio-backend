from fastapi import FastAPI
from app.api.v1 import health, users, rooms, auth

app = FastAPI(title="Spatial Audio Backend")

app.include_router(health.router)
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

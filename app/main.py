from fastapi import FastAPI
from app.api.v1 import health, users, rooms

app = FastAPI(title="Spatial Audio Backend")

app.include_router(health.router)
app.include_router(users.router, prefix="/users", tags=["Users"])
#app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])


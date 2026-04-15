"""Application factory — middleware and router registration only."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers.auth import router as auth_router
from routers.weather import router as weather_router

app = FastAPI(title="Weather API")

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True,
)

app.include_router(auth_router)
app.include_router(weather_router)

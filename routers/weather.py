"""Weather and news router."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from auth_utils import get_current_user
from models import (
  CurrentWeatherResponse,
  ForecastDetailResponse,
  ForecastResponse,
  NewsResponse,
)
from services.news_service import fetch_weather_news
from services.weather_service import (
  fetch_current_weather,
  fetch_forecast,
  fetch_forecast_detail,
)

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
  city: Optional[str] = Query(None),
  lat: Optional[float] = Query(None),
  lon: Optional[float] = Query(None),
  _: str = Depends(get_current_user),
):
  """Return current weather for a city name or lat/lon coordinates."""
  return await fetch_current_weather(city, lat, lon)


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
  city: Optional[str] = Query(None),
  lat: Optional[float] = Query(None),
  lon: Optional[float] = Query(None),
  _: str = Depends(get_current_user),
):
  """Return a 5-day daily forecast for a city name or lat/lon coordinates."""
  return await fetch_forecast(city, lat, lon)


@router.get("/forecast/detail", response_model=ForecastDetailResponse)
async def get_forecast_detail(
  date: str = Query(...),
  city: Optional[str] = Query(None),
  lat: Optional[float] = Query(None),
  lon: Optional[float] = Query(None),
  _: str = Depends(get_current_user),
):
  """Return all 3-hour slots for a specific date."""
  return await fetch_forecast_detail(city, lat, lon, date)


@router.get("/news", response_model=NewsResponse)
async def get_weather_news(
  city: Optional[str] = Query(None),
  _: str = Depends(get_current_user),
):
  """Return recent weather-related news articles, optionally filtered by city."""
  return await fetch_weather_news(city)

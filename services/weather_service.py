"""OpenWeatherMap API calls."""

from typing import Optional

import httpx
from fastapi import HTTPException

from config import settings


async def fetch_current_weather(
  city: Optional[str],
  lat: Optional[float],
  lon: Optional[float],
) -> dict:
  """
  Fetch current weather from OpenWeatherMap.

  Raises HTTPException on API errors or missing location parameters.
  """
  if not settings.openweather_api_key:
    raise HTTPException(status_code=500, detail="Weather API key not configured")

  params = {"appid": settings.openweather_api_key, "units": "metric"}
  if lat is not None and lon is not None:
    params.update({"lat": lat, "lon": lon})
  elif city:
    params["q"] = city
  else:
    raise HTTPException(status_code=400, detail="Provide either city or lat/lon")

  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{settings.openweather_base_url}/weather", params=params)

  if resp.status_code == 404:
    raise HTTPException(status_code=404, detail=f"City '{city}' not found")
  if resp.status_code != 200:
    raise HTTPException(status_code=resp.status_code, detail="Weather API error")

  data = resp.json()
  return {
    "city": data["name"],
    "country": data["sys"]["country"],
    "lat": data["coord"]["lat"],
    "lon": data["coord"]["lon"],
    "temp": data["main"]["temp"],
    "feels_like": data["main"]["feels_like"],
    "humidity": data["main"]["humidity"],
    "description": data["weather"][0]["description"],
    "icon": data["weather"][0]["icon"],
    "wind_speed": data["wind"]["speed"],
    "visibility": data.get("visibility", 0) // 1000,
  }


async def fetch_forecast(
  city: Optional[str],
  lat: Optional[float],
  lon: Optional[float],
) -> dict:
  """
  Fetch a 5-day daily forecast from OpenWeatherMap.

  Returns one entry per day with running min/max temps.
  """
  if not settings.openweather_api_key:
    raise HTTPException(status_code=500, detail="Weather API key not configured")

  params = {"appid": settings.openweather_api_key, "units": "metric", "cnt": 40}
  if lat is not None and lon is not None:
    params.update({"lat": lat, "lon": lon})
  elif city:
    params["q"] = city
  else:
    raise HTTPException(status_code=400, detail="Provide either city or lat/lon")

  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{settings.openweather_base_url}/forecast", params=params)

  if resp.status_code == 404:
    raise HTTPException(status_code=404, detail=f"City '{city}' not found")
  if resp.status_code != 200:
    raise HTTPException(status_code=resp.status_code, detail="Weather API error")

  data = resp.json()
  daily: dict = {}
  for item in data["list"]:
    date = item["dt_txt"].split(" ")[0]
    if date not in daily:
      daily[date] = {
        "date": date,
        "temp_min": item["main"]["temp_min"],
        "temp_max": item["main"]["temp_max"],
        "description": item["weather"][0]["description"],
        "icon": item["weather"][0]["icon"],
      }
    else:
      daily[date]["temp_min"] = min(daily[date]["temp_min"], item["main"]["temp_min"])
      daily[date]["temp_max"] = max(daily[date]["temp_max"], item["main"]["temp_max"])

  return {"city": data["city"]["name"], "forecast": list(daily.values())[:5]}


async def fetch_forecast_detail(
  city: Optional[str],
  lat: Optional[float],
  lon: Optional[float],
  date: str,
) -> dict:
  """Fetch all 3-hour slots for a specific *date* from the forecast endpoint."""
  if not settings.openweather_api_key:
    raise HTTPException(status_code=500, detail="Weather API key not configured")

  params = {"appid": settings.openweather_api_key, "units": "metric", "cnt": 40}
  if lat is not None and lon is not None:
    params.update({"lat": lat, "lon": lon})
  elif city:
    params["q"] = city
  else:
    raise HTTPException(status_code=400, detail="Provide either city or lat/lon")

  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{settings.openweather_base_url}/forecast", params=params)

  if resp.status_code != 200:
    raise HTTPException(status_code=resp.status_code, detail="Weather API error")

  data = resp.json()
  slots = [
    {
      "time": item["dt_txt"].split(" ")[1][:5],
      "temp": item["main"]["temp"],
      "feels_like": item["main"]["feels_like"],
      "humidity": item["main"]["humidity"],
      "description": item["weather"][0]["description"],
      "icon": item["weather"][0]["icon"],
      "wind_speed": item["wind"]["speed"],
      "pop": round(item.get("pop", 0) * 100),
    }
    for item in data["list"]
    if item["dt_txt"].startswith(date)
  ]
  return {"date": date, "slots": slots}

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Weather API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def check_api_key():
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")


@app.get("/weather/current")
async def get_current_weather(city: str = Query(..., description="City name")):
    check_api_key()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/weather",
            params={"q": city, "appid": API_KEY, "units": "metric"},
        )
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


@app.get("/weather/forecast")
async def get_forecast(city: str = Query(..., description="City name")):
    check_api_key()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/forecast",
            params={"q": city, "appid": API_KEY, "units": "metric", "cnt": 40},
        )
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Weather API error")

    data = resp.json()
    # Pick one entry per day (noon time)
    daily = {}
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

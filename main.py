from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Weather API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24 hours
BASE_URL = "https://api.openweathermap.org/data/2.5"
NEWS_URL = "https://newsapi.org/v2/everything"

# ── Auth setup ──
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory user store (replace with a DB in production)
users_db: dict = {}

class UserRegister(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Auth endpoints ──
@app.post("/auth/register", status_code=201)
async def register(body: UserRegister):
    if body.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    users_db[body.username] = hash_password(body.password)
    token = create_token(body.username)
    return {"access_token": token, "token_type": "bearer", "username": body.username}

@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_hash = users_db.get(form.username)
    if not user_hash or not verify_password(form.password, user_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(form.username)
    return {"access_token": token, "token_type": "bearer", "username": form.username}

@app.get("/auth/me")
async def me(username: str = Depends(get_current_user)):
    return {"username": username}


def check_api_key():
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")


@app.get("/weather/current")
async def get_current_weather(
    city: str = Query(None),
    lat: float = Query(None),
    lon: float = Query(None),
    _: str = Depends(get_current_user),
):
    check_api_key()
    if lat is not None and lon is not None:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    elif city:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
    else:
        raise HTTPException(status_code=400, detail="Provide either city or lat/lon")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/weather", params=params)
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
async def get_forecast(
    city: str = Query(None),
    lat: float = Query(None),
    lon: float = Query(None),
    _: str = Depends(get_current_user),
):
    check_api_key()
    if lat is not None and lon is not None:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "cnt": 40}
    elif city:
        params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": 40}
    else:
        raise HTTPException(status_code=400, detail="Provide either city or lat/lon")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/forecast", params=params)
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


@app.get("/weather/news")
async def get_weather_news(city: str = Query(None), _: str = Depends(get_current_user)):
    if not NEWS_API_KEY:
        raise HTTPException(status_code=500, detail="News API key not configured")

    query = f"weather {city}" if city else "weather"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
            },
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"News API error: {resp.text}")

    data = resp.json()
    articles = []
    for a in data.get("articles", []):
        title = a.get("title", "")
        url = a.get("url", "")
        if not title or not url:
            continue
        if "[Removed]" in title or "[Removed]" in url:
            continue
        articles.append({
            "title": title,
            "description": a.get("description") or "",
            "url": url,
            "image": a.get("urlToImage"),
            "source": a.get("source", {}).get("name", "Unknown"),
            "published_at": a.get("publishedAt", ""),
        })
        if len(articles) == 6:
            break

    return {"articles": articles}


@app.get("/weather/forecast/detail")
async def get_forecast_detail(
    city: str = Query(None),
    lat: float = Query(None),
    lon: float = Query(None),
    date: str = Query(...),
    _: str = Depends(get_current_user),
):
    check_api_key()
    if lat is not None and lon is not None:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "cnt": 40}
    elif city:
        params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": 40}
    else:
        raise HTTPException(status_code=400, detail="Provide either city or lat/lon")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/forecast", params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Weather API error")

    data = resp.json()
    slots = []
    for item in data["list"]:
        if item["dt_txt"].startswith(date):
            slots.append({
                "time": item["dt_txt"].split(" ")[1][:5],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"],
                "wind_speed": item["wind"]["speed"],
                "pop": round(item.get("pop", 0) * 100),
            })
    return {"date": date, "slots": slots}

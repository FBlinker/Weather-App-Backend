"""Pydantic request/response models."""

from pydantic import BaseModel
from typing import Optional, List


# ── Auth models ──────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
  username: str
  password: str


class TokenResponse(BaseModel):
  access_token: str
  token_type: str
  username: str


class UserResponse(BaseModel):
  username: str


# ── Weather models ────────────────────────────────────────────────────────────

class CurrentWeatherResponse(BaseModel):
  city: str
  country: str
  lat: float
  lon: float
  temp: float
  feels_like: float
  humidity: int
  description: str
  icon: str
  wind_speed: float
  visibility: int


class ForecastDay(BaseModel):
  date: str
  temp_min: float
  temp_max: float
  description: str
  icon: str


class ForecastResponse(BaseModel):
  city: str
  forecast: List[ForecastDay]


class HourlySlot(BaseModel):
  time: str
  temp: float
  feels_like: float
  humidity: int
  description: str
  icon: str
  wind_speed: float
  pop: int


class ForecastDetailResponse(BaseModel):
  date: str
  slots: List[HourlySlot]


# ── News models ───────────────────────────────────────────────────────────────

class NewsArticle(BaseModel):
  title: str
  description: str
  url: str
  image: Optional[str]
  source: str
  published_at: str


class NewsResponse(BaseModel):
  articles: List[NewsArticle]

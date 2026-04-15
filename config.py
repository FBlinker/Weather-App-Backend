"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
  openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
  news_api_key: str = os.getenv("NEWS_API_KEY", "")
  jwt_secret: str = os.getenv("JWT_SECRET", "changeme")
  jwt_algorithm: str = "HS256"
  jwt_expire_minutes: int = 60 * 24

  google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
  google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
  frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
  backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")

  openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
  google_auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
  google_token_url: str = "https://oauth2.googleapis.com/token"
  google_userinfo_url: str = "https://www.googleapis.com/oauth2/v3/userinfo"

  users_file: str = "users.json"

  cors_origins: list = [
    "http://localhost:5173",
    "http://localhost:5174",
  ]


settings = Settings()

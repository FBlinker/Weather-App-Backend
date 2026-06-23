# ⛅ Weather App

A full-stack weather application built with **FastAPI** and **Vue 3**, featuring real-time weather data, 5-day forecasts, an interactive map, weather news, and JWT-based authentication.

![Vue 3](https://img.shields.io/badge/Vue-3.x-42b883?logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## ✨ Features

- 🔐 **Authentication** — Register/login with JWT, Google OAuth support
- 📍 **Geolocation** — Auto-detect current location on login
- 🌡 **Current Weather** — Temperature, humidity, wind speed, visibility
- 📅 **5-Day Forecast** — Daily summary with clickable hourly detail modal
- 🗺 **Interactive Map** — Leaflet.js map centered on the searched city
- 📰 **Weather News** — Latest news articles via NewsAPI
- ⭐ **Favorites** — Save and manage favorite cities (persisted in localStorage)
- 🌙 **Dark / Light Mode** — Toggle with smooth transitions
- 📱 **Responsive** — Works on desktop, tablet, and mobile

---

## 🏗 Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | Vue 3, Vite, Axios, Leaflet.js      |
| Backend   | FastAPI, Uvicorn, httpx             |
| Auth      | JWT (python-jose), passlib, Google OAuth 2.0 |
| APIs      | OpenWeatherMap, NewsAPI             |

---

## 📁 Project Structure

```
weather-app/
├── backend/
│   ├── main.py                  # App factory
│   ├── config.py                # Settings from env vars
│   ├── models.py                # Pydantic schemas
│   ├── auth_utils.py            # JWT & password helpers
│   ├── routers/
│   │   ├── auth.py              # /auth endpoints
│   │   └── weather.py           # /weather endpoints
│   ├── services/
│   │   ├── weather_service.py   # OpenWeatherMap calls
│   │   └── news_service.py      # NewsAPI calls
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   ├── services/
    │   │   └── api.js           # Axios instance + API functions
    │   ├── composables/
    │   │   ├── useAuth.js
    │   │   ├── useWeather.js
    │   │   ├── useGeolocation.js
    │   │   └── useFavorites.js
    │   └── components/
    │       ├── AuthPage.vue
    │       ├── SearchBar.vue
    │       ├── WeatherCard.vue
    │       ├── ForecastCard.vue
    │       ├── MapView.vue
    │       ├── NewsCard.vue
    │       ├── FavoritesModal.vue
    │       └── Favorites.vue
    ├── package.json
    └── vite.config.js
```
---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- API keys for [OpenWeatherMap](https://openweathermap.org/api) and [NewsAPI](https://newsapi.org)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weather-app.git
cd weather-app
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
OPENWEATHER_API_KEY=your_openweathermap_key
NEWS_API_KEY=your_newsapi_key
JWT_SECRET=your_random_secret_string
GOOGLE_CLIENT_ID=your_google_client_id       # optional
GOOGLE_CLIENT_SECRET=your_google_client_secret # optional
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🔑 Environment Variables

| Variable               | Required | Description                              |
|------------------------|----------|------------------------------------------|
| `OPENWEATHER_API_KEY`  | ✅       | OpenWeatherMap API key                   |
| `NEWS_API_KEY`         | ✅       | NewsAPI key                              |
| `JWT_SECRET`           | ✅       | Secret string for signing JWTs           |
| `GOOGLE_CLIENT_ID`     | ⬜       | Google OAuth client ID                   |
| `GOOGLE_CLIENT_SECRET` | ⬜       | Google OAuth client secret               |
| `FRONTEND_URL`         | ⬜       | Frontend origin (default: localhost:5173)|
| `BACKEND_URL`          | ⬜       | Backend origin (default: localhost:8000) |

---

## 🔌 API Endpoints

### Auth

| Method | Endpoint                  | Description                  |
|--------|---------------------------|------------------------------|
| POST   | `/auth/register`          | Create a new account         |
| POST   | `/auth/login`             | Sign in, returns JWT         |
| GET    | `/auth/me`                | Get current user info        |
| GET    | `/auth/google`            | Redirect to Google OAuth     |
| GET    | `/auth/google/callback`   | Google OAuth callback        |

### Weather *(requires Bearer token)*

| Method | Endpoint                    | Description                        |
|--------|-----------------------------|------------------------------------|
| GET    | `/weather/current`          | Current weather by city or coords  |
| GET    | `/weather/forecast`         | 5-day daily forecast               |
| GET    | `/weather/forecast/detail`  | Hourly slots for a specific date   |
| GET    | `/weather/news`             | Weather news articles              |

---

## 🔐 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → **APIs & Services** → **Credentials**
3. Click **Create OAuth 2.0 Client ID** → Web application
4. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
5. Copy the Client ID and Secret into your `.env`

---

## 📸 Screenshots

> Dark mode · Light mode · Forecast detail modal · Favorites

---

## 📄 License

MIT © 2026

"""NewsAPI calls."""

from typing import Optional

import httpx
from fastapi import HTTPException

from config import settings


async def fetch_weather_news(city: Optional[str]) -> dict:
  """
  Fetch weather-related news articles from NewsAPI.

  Returns up to 6 cleaned articles. Raises HTTPException on API errors.
  """
  if not settings.news_api_key:
    raise HTTPException(status_code=500, detail="News API key not configured")

  query = f"weather {city}" if city else "weather"

  async with httpx.AsyncClient() as client:
    resp = await client.get(
      "https://newsapi.org/v2/everything",
      params={
        "q": query,
        "apiKey": settings.news_api_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
      },
    )

  if resp.status_code != 200:
    raise HTTPException(
      status_code=resp.status_code,
      detail=f"News API error: {resp.text}",
    )

  articles = []
  for item in resp.json().get("articles", []):
    title = item.get("title", "")
    url = item.get("url", "")
    if not title or not url:
      continue
    if "[Removed]" in title or "[Removed]" in url:
      continue
    articles.append({
      "title": title,
      "description": item.get("description") or "",
      "url": url,
      "image": item.get("urlToImage"),
      "source": item.get("source", {}).get("name", "Unknown"),
      "published_at": item.get("publishedAt", ""),
    })
    if len(articles) == 6:
      break

  return {"articles": articles}

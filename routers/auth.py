"""Authentication router — register, login, /me, and Google OAuth."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

import httpx

from auth_utils import (
  create_token,
  get_current_user,
  hash_password,
  load_users,
  random_password,
  save_users,
  verify_password,
)
from config import settings
from models import TokenResponse, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# User store — loaded once at startup, persisted on every write.
users_db: dict = load_users()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: UserRegister):
  """Create a new local account and return a JWT."""
  if body.username in users_db:
    raise HTTPException(status_code=400, detail="Username already exists")
  if len(body.password) < 6:
    raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

  users_db[body.username] = hash_password(body.password)
  save_users(users_db)

  token = create_token(body.username)
  return TokenResponse(access_token=token, token_type="bearer", username=body.username)


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
  """Authenticate with username/password and return a JWT."""
  user_hash = users_db.get(form.username)
  if not user_hash or not verify_password(form.password, user_hash):
    raise HTTPException(status_code=401, detail="Invalid username or password")

  token = create_token(form.username)
  return TokenResponse(access_token=token, token_type="bearer", username=form.username)


@router.get("/me", response_model=UserResponse)
async def me(username: str = Depends(get_current_user)):
  """Return the currently authenticated user's info."""
  return UserResponse(username=username)


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google")
async def google_login():
  """Redirect the browser to Google's OAuth consent screen."""
  if not settings.google_client_id:
    raise HTTPException(status_code=500, detail="Google OAuth not configured")

  params = {
    "client_id": settings.google_client_id,
    "redirect_uri": f"{settings.backend_url}/auth/google/callback",
    "response_type": "code",
    "scope": "openid email profile",
    "access_type": "offline",
  }
  query_string = "&".join(f"{k}={v}" for k, v in params.items())
  return RedirectResponse(f"{settings.google_auth_url}?{query_string}")


@router.get("/google/callback")
async def google_callback(code: str = Query(...)):
  """Exchange the Google auth code for a JWT and redirect to the frontend."""
  if not settings.google_client_id or not settings.google_client_secret:
    raise HTTPException(status_code=500, detail="Google OAuth not configured")

  async with httpx.AsyncClient() as client:
    token_resp = await client.post(
      settings.google_token_url,
      data={
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": f"{settings.backend_url}/auth/google/callback",
        "grant_type": "authorization_code",
      },
    )
    if token_resp.status_code != 200:
      raise HTTPException(status_code=400, detail="Failed to exchange Google code")

    google_access_token = token_resp.json().get("access_token")

    user_resp = await client.get(
      settings.google_userinfo_url,
      headers={"Authorization": f"Bearer {google_access_token}"},
    )
    if user_resp.status_code != 200:
      raise HTTPException(status_code=400, detail="Failed to get Google user info")

    user_info = user_resp.json()

  username = user_info.get("email", "").split("@")[0]
  google_id = user_info.get("sub")
  user_key = f"google:{google_id}"

  if user_key not in users_db:
    users_db[user_key] = hash_password(random_password())
    save_users(users_db)

  jwt_token = create_token(username)
  return RedirectResponse(
    f"{settings.frontend_url}?token={jwt_token}&username={username}"
  )

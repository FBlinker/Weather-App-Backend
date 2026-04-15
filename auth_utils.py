"""JWT creation/verification and password hashing helpers."""

import json
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
  """Return a hash of *password*."""
  return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
  """Return True if *plain* matches *hashed*."""
  return pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_token(username: str) -> str:
  """Create a signed JWT for *username* that expires after the configured TTL."""
  expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
  payload = {"sub": username, "exp": expire}
  return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
  """FastAPI dependency — decode the bearer token and return the username."""
  try:
    payload = jwt.decode(
      token,
      settings.jwt_secret,
      algorithms=[settings.jwt_algorithm],
    )
    username: Optional[str] = payload.get("sub")
    if not username:
      raise HTTPException(status_code=401, detail="Invalid token")
    return username
  except JWTError:
    raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── User store (file-persisted) ───────────────────────────────────────────────

def load_users() -> dict:
  """Load the user database from disk, returning an empty dict on failure."""
  try:
    with open(settings.users_file, "r") as f:
      return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    return {}


def save_users(db: dict) -> None:
  """Persist the user database to disk."""
  with open(settings.users_file, "w") as f:
    json.dump(db, f)


def random_password() -> str:
  """Generate a cryptographically random placeholder password."""
  return secrets.token_hex(32)

import logging
import re
from datetime import timedelta

from django.contrib.auth import authenticate
from django.conf import settings
from django.core.cache import cache
from ninja import Router
from ninja.security import HttpBearer
from ninja_jwt.tokens import RefreshToken
from ninja.errors import HttpError

from authentication.models import User
from authentication.schemas import (
    RegisterIn,
    LoginIn,
    TokenOut,
    RefreshIn,
    RefreshOut,
    UserOut,
)

logger = logging.getLogger(__name__)
router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        from ninja_jwt.tokens import AccessToken
        if not token:
            token = request.GET.get("token", "")
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)
            request.user = user
            return user
        except Exception:
            return None


auth = AuthBearer()


def check_rate_limit(key: str, limit: int = 5, period: int = 300) -> None:
    """Check rate limit for a given key (IP, email, etc.)"""
    attempts = cache.get(key, 0)
    if attempts >= limit:
        raise HttpError(429, f"Too many attempts. Try again in {period // 60} minutes.")
    cache.set(key, attempts + 1, period)


def validate_password(password: str) -> str:
    """Validate password strength"""
    if len(password) < 8:
        raise HttpError(400, "Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise HttpError(400, "Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise HttpError(400, "Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise HttpError(400, "Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HttpError(400, "Password must contain at least one special character.")
    return password


@router.post("/register", response=TokenOut, tags=["Auth"])
def register(request, payload: RegisterIn):
    # Rate limit by IP
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    check_rate_limit(f"register_{ip}", limit=3, period=3600)
    
    # Check if email already exists
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already registered.")
    
    # Check if username already exists
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already taken.")
    
    # Validate password strength
    validate_password(payload.password)
    
    # Create user
    user = User.objects.create_user(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        role=payload.role or "operator",
    )
    
    refresh = RefreshToken.for_user(user)
    
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
    }


@router.post("/login", response=TokenOut, tags=["Auth"])
def login(request, payload: LoginIn):
    # Rate limit by IP + email combination
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    rate_limit_key = f"login_{ip}_{payload.email.lower()}"
    check_rate_limit(rate_limit_key, limit=5, period=300)
    
    # Check if account is locked
    lock_key = f"lockout_{payload.email.lower()}"
    if cache.get(lock_key, False):
        raise HttpError(403, "Account temporarily locked. Try again later.")
    
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        # Generic error message for security (don't reveal if email exists)
        raise HttpError(401, "Invalid email or password.")
    
    if not user.check_password(payload.password):
        # Track failed attempts
        fail_key = f"failures_{payload.email.lower()}"
        failures = cache.get(fail_key, 0) + 1
        cache.set(fail_key, failures, 900)  # 15 minutes window
        
        # Lock account after 5 failures
        if failures >= 5:
            cache.set(lock_key, True, 900)  # Lock for 15 minutes
            cache.delete(fail_key)
            raise HttpError(403, "Account locked due to too many failed attempts. Try again later.")
        
        raise HttpError(401, "Invalid email or password.")
    
    # Reset failure count on successful login
    cache.delete(f"failures_{payload.email.lower()}")
    cache.delete(lock_key)
    
    # Check if user is active
    if not user.is_active:
        raise HttpError(403, "Account is disabled.")
    
    refresh = RefreshToken.for_user(user)
    
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
    }


@router.post("/refresh", response=RefreshOut, tags=["Auth"])
def refresh_token(request, payload: RefreshIn):
    try:
        refresh = RefreshToken(payload.refresh)
        return {"access": str(refresh.access_token)}
    except Exception:
        raise HttpError(401, "Invalid or expired refresh token.")


@router.get("/me", response=UserOut, auth=auth, tags=["Auth"])
def me(request):
    return request.user
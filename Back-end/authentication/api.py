import logging
from datetime import timedelta

from django.contrib.auth import authenticate
from django.conf import settings
from ninja import Router
from ninja.security import HttpBearer
from ninja_jwt.tokens import RefreshToken

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


@router.post("/register", response=TokenOut, tags=["Auth"])
def register(request, payload: RegisterIn):
    if User.objects.filter(email=payload.email).exists():
        from ninja.errors import HttpError
        raise HttpError(400, "Email already registered.")

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
    from ninja.errors import HttpError

    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:

        raise HttpError(401, "Invalid email or password.")

    if not user.check_password(payload.password):
        raise HttpError(401, "Invalid email or password.")



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
    from ninja.errors import HttpError
    try:
        refresh = RefreshToken(payload.refresh)
        return {"access": str(refresh.access_token)}
    except Exception:
        raise HttpError(401, "Invalid or expired refresh token.")


@router.get("/me", response=UserOut, auth=auth, tags=["Auth"])
def me(request):
    return request.user
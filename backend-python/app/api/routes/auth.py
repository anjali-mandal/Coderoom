from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut
from app.services.auth_service import get_user_by_id, login_user, register_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest):
    try:
        return await register_user(payload.name, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    try:
        return await login_user(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/me", response_model=UserOut)
async def current_user(current_user: dict = Depends(get_current_user)):
    user = await get_user_by_id(current_user.get("userId", ""))
    if not user:
        raise HTTPException(status_code=401, detail="User account no longer exists")
    return user

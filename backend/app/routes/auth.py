from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.auth_service import create_owner_token, validate_owner_token, verify_owner_credentials


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginPayload):
    if not verify_owner_credentials(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid owner credentials")

    token = create_owner_token(payload.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "owner": {"username": payload.username},
    }


@router.get("/me")
def me(request: Request):
    owner = getattr(request.state, "owner", None)
    if not owner:
        raise HTTPException(status_code=401, detail="Owner login required")

    return {"authenticated": True, "owner": owner}


@router.post("/logout")
def logout(request: Request):
    owner = getattr(request.state, "owner", None)
    if not owner:
        raise HTTPException(status_code=401, detail="Owner login required")

    return {"ok": True}
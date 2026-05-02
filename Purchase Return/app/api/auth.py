from fastapi import APIRouter, HTTPException

from app.operations.utils import create_jwt_token
from app.schema.auth import TokenResponse


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(username: str, password: str):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    return TokenResponse(access_token=create_jwt_token(username))

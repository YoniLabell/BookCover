from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...core.security import FAKE_USERS, TokenResponse, create_access_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    user = FAKE_USERS.get(form_data.username)
    if not user or form_data.password != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(subject=user.username, expires_delta=timedelta(hours=12))
    return TokenResponse(access_token=token)

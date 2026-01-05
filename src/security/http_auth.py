import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

security = HTTPBasic()

def raise_not_authorized():
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )

def check_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = os.environ['API_USER'].encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.environ['API_PWD'].encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise_not_authorized()

    return credentials.username

def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    """Get current user from credentials after validation"""
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = os.environ['API_USER'].encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.environ['API_PWD'].encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise_not_authorized()

    return credentials.username
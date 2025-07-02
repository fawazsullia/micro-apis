# auth_helpers.py
from fastapi.responses import Response

def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600
    )

def clear_auth_cookie(response: Response):
    response.delete_cookie("access_token")

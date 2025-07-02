# dependencies.py
from fastapi import Request, HTTPException, Depends
from utils.jwt import decode_token
from schemas import UserModel

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        user = await UserModel.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# main.py or routes/auth.py
from fastapi import FastAPI, HTTPException, APIRouter, Request
from schemas import UserModel
from models import UserCreate, UserRead, UserLogin
from utils import verify_password
from datetime import datetime
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from utils.jwt import create_access_token, decode_token
from utils.cookie import set_auth_cookie, clear_auth_cookie
from fastapi.responses import Response
from config import settings

oauth = OAuth()

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

app = APIRouter()

@app.post("/register", response_model=UserRead)
async def register(user: UserCreate):
    existing = await UserModel.find_one(UserModel.email == user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    if(user.password != user.confirm_password):
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    new_user = UserModel(name=user.name, email=user.email)
    await new_user.set_password(user.password)
    await new_user.create()
    return UserRead(id=str(new_user.id), email=new_user.email, created_at=new_user.created_at)

@app.post("/login")
async def login(user: UserLogin, response: Response):
    db_user = await UserModel.find_one(UserModel.email == user.email)
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(db_user.id)})
    set_auth_cookie(response, token)

    return {"message": "Login successful", "user_id": str(db_user.id)}

@app.get("/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/google/callback")
async def auth_google_callback(request: Request, response: Response):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    # Check or create user
    user = await UserModel.find_one(UserModel.email == user_info['email'])
    if not user:
        user = UserModel(
            name=user_info['email'],
            password_hash=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await user.create()
    
    jwt_token = create_access_token({"sub": str(user.id)})
    set_auth_cookie(response, jwt_token)

    return {"message": "Google login successful", "user": user.name}

@app.post("/logout")
def logout(response: Response):
    clear_auth_cookie(response)
    return {"message": "Logged out"}

@app.get("/me", response_model=UserRead)
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
        return UserRead(id=str(user.id), name=user.name, email=user.email, created_at=user.created_at)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

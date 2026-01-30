import logging

import gradio as gr
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import auth, models, schemas
from app.cache import cache_response
from app.config import API_V1_STR, PROJECT_NAME, SECRET_KEY
from app.database import engine, get_db
from app.worker import send_welcome_email

# Initialize Database
models.Base.metadata.create_all(bind=engine)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Create App
app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
    docs_url=f"{API_V1_STR}/docs",
    redoc_url=f"{API_V1_STR}/redoc"
)

# Mount Gradio App
from main import demo

app = gr.mount_gradio_app(app, demo, path="/ui")

# Instrument Prometheus
Instrumentator().instrument(app).expose(app)

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Routes ---

@app.post(f"{API_V1_STR}/register", response_model=schemas.User)
@limiter.limit("5/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = auth.create_user(db=db, user=user)

    # Trigger background task
    try:
        send_welcome_email.delay(user.email)
    except Exception as e:
        logger.error(f"Failed to queue welcome email: {e}")

    return new_user

@app.post(f"{API_V1_STR}/token", response_model=schemas.Token)
@limiter.limit("10/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get(f"{API_V1_STR}/users/me", response_model=schemas.User)
def read_users_me(request: Request, current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# --- OAuth Routes ---

@app.get(f"{API_V1_STR}/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await auth.oauth.google.authorize_redirect(request, redirect_uri)

@app.get(f"{API_V1_STR}/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    token = await auth.oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    if not user_info:
         user_info = await auth.oauth.google.userinfo(token=token)

    email = user_info.get('email')
    user = auth.get_user_by_email(db, email)
    if not user:
        user = auth.create_oauth_user(db, email, "google")

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get(f"{API_V1_STR}/login/github")
async def login_github(request: Request):
    redirect_uri = request.url_for('auth_github')
    return await auth.oauth.github.authorize_redirect(request, redirect_uri)

@app.get(f"{API_V1_STR}/auth/github")
async def auth_github(request: Request, db: Session = Depends(get_db)):
    token = await auth.oauth.github.authorize_access_token(request)
    resp = await auth.oauth.github.get('user', token=token)
    profile = resp.json()
    email = profile.get('email')

    # Github email might be private, need another call if None (omitted for brevity)
    if not email:
         raise HTTPException(status_code=400, detail="Could not retrieve email from GitHub")

    user = auth.get_user_by_email(db, email)
    if not user:
        user = auth.create_oauth_user(db, email, "github")

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Health Check ---
@app.get("/health")
@cache_response(expire=10)
async def health_check():
    return {"status": "ok"}

# --- WebSocket ---
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for demonstration
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

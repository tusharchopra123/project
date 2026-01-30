
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import init_db
from .routers import auth, portfolio
from .middleware.auth_middleware import AuthMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title="WealthTrack API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (Allow Frontend)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Middleware (Custom)
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(auth.router)
app.include_router(portfolio.router)

@app.get("/")
def read_root():
    return {"message": "WealthTrack API is running (MVC Mode)"}

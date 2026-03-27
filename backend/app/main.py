from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, audio, analysis
from app.core.database import connect_db, disconnect_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EchoShield API",
    description="Real-Time AI Scammer Interceptor Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_db()
    logger.info("EchoShield backend started.")


@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()
    logger.info("EchoShield backend stopped.")


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(audio.router, tags=["Audio Processing"])
app.include_router(analysis.router, tags=["Analysis"])


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "EchoShield", "version": "1.0.0"}

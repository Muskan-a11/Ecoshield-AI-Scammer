from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="EchoShield API")

@app.get("/")
def root():
    return {"message": "EchoShield API Running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
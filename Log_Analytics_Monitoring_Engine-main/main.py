from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.router import service

app = FastAPI(
    title="Log Analytics Monitoring API",
    description="Backend API for Log Processing and Anomaly Detection",
    version="1.0.0"
)

# ✅ CORS Configuration (Allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace "*" with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root endpoint (So / doesn't give 404)
@app.get("/")
def home():
    return {"message": "Log Analytics Backend Running Successfully 🚀"}

# ✅ Include your router
app.include_router(service.router)

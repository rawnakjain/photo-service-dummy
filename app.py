from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.service_routes import router as service_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Salon Services Extraction API",
    description="Extract salon services from menu images using Gemini Flash",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(service_router, prefix="/api/v1", tags=["services"])

@app.get("/")
async def root():
    return {"message": "Salon Services Extraction API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "salon-services-extraction"}
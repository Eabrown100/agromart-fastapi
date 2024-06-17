from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import farmer, buyer, auth, weather, analytics, payment, mobile_money, upload

# Ensure database tables are created
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary for your frontend origins
    allow_credentials=True,
    allow_methods=["*"],   # Adjust as necessary for allowed HTTP methods
    allow_headers=["*"],   # Adjust as necessary for allowed headers
)

# Include routers for different functionalities
app.include_router(farmer.router, prefix="/farmers", tags=["Farmers"])
app.include_router(buyer.router, prefix="/buyers", tags=["Buyers"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(weather.router, prefix="/weather", tags=["Weather"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(payment.router)  # Include without prefix or tags if not needed
app.include_router(mobile_money.router)  # Include without prefix or tags if not needed
app.include_router(upload.router)  # Include without prefix or tags if not needed

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Agri-Ecommerce API"}

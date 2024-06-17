from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

API_KEY = "your_weather_api_key"
BASE_URL = "http://api.weatherapi.com/v1/current.json"

@router.get("/forecast")
def get_weather(city: str):
    try:
        response = requests.get(BASE_URL, params={"key": API_KEY, "q": city})
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail="Error fetching weather data")
    return response.json()

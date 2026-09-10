from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

app = FastAPI()

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"


@app.get("/add")
def predict_price(area: float, bedrooms: int, location: str) -> float:
    base_price = 500000000
    price_per_sqft = 15000000  # Price per square foot
    bedroom_multiplier = 50000000  # Additional price per bedroom

    location_factor = {
        "hanoi": 1.3,
        "hcmc": 1.25,
    }

    # Calculate the price
    location_multiplier = location_factor.get(location.lower(), 1.0)
    price = (base_price + (area * price_per_sqft) + (bedrooms * bedroom_multiplier)) * location_multiplier

    return price


@app.get("/predict")
def predict(area: float, bedrooms: int, location: str = "other"):
    predicted_price = predict_price(area, bedrooms, location)
    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": predicted_price,
    }


@app.post("/predict")
def predict_from_body(house: HouseInput):
    predicted_price = predict_price(house.area, house.bedrooms, house.location)
    return {
        "area": house.area,
        "bedrooms": house.bedrooms,
        "location": house.location,
        "predicted_price": predicted_price,
    }

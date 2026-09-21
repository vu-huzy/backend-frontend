from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
def read_root():
    return FileResponse(frontend_dir / "index.html")


@app.get("/predict")
def predict(area: float, bedrooms: int, location: str = "other"):
    location_multiplier = {"hanoi": 1.3, "hcmc": 1.25}.get(location.lower(), 1.0)
    predicted_price = (
        500_000_000 + area * 15_000_000 + bedrooms * 50_000_000
    ) * location_multiplier
    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": predicted_price,
    }


@app.get("/items/me")
def read_item_me():
    return {"item_id": "This is my item"}


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


class ItemPublic(BaseModel):
    id: int
    name: str
    price: float


class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int


items_db = {
    1: {"id": 1, "name": "Ban", "price": 2000, "secret": "xyz"},
    2: {"id": 2, "name": "Ghe", "price": 1500, "secret": "abc"},
}
_next_id = 3


def _find(item_id: int) -> dict | None:
    return items_db.get(item_id)


def _name_taken(name: str, exclude_id: int | None = None) -> bool:
    lowered = name.lower()
    return any(
        item["name"].lower() == lowered and item["id"] != exclude_id
        for item in items_db.values()
    )


@app.get("/items", response_model=ItemListResponse)
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_price: float | None = None,
    max_price: float | None = None,
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    results = list(items_db.values())

    if min_price is not None:
        results = [item for item in results if item["price"] >= min_price]
    if max_price is not None:
        results = [item for item in results if item["price"] <= max_price]
    if q is not None:
        search_text = q.lower()
        results = [item for item in results if search_text in item["name"].lower()]

    results.sort(key=lambda item: item[sort_by], reverse=(order == "desc"))

    # total is counted after filtering but before slicing
    return {
        "items": results[skip : skip + limit],
        "total": len(results),
        "skip": skip,
        "limit": limit,
    }


@app.get("/items/{item_id}", response_model=ItemPublic)
def read_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
    global _next_id
    if _name_taken(data.name):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    new_id = _next_id
    _next_id += 1
    saved_item = {
        "id": new_id,
        "name": data.name,
        "price": data.price,
        "secret": "xyz",
    }
    items_db[new_id] = saved_item
    return saved_item


@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemCreate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if _name_taken(data.name, exclude_id=item_id):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    item.update({"name": data.name, "price": data.price})
    return item


@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, data: ItemUpdate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    changes = data.model_dump(exclude_unset=True)

    if "name" in changes and _name_taken(changes["name"], exclude_id=item_id):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    item.update(changes)
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    del items_db[item_id]
    return None


class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float


class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"


@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(data: HousePriceRequest):
    # Fake formula; swap for model.predict(...) once a real model exists.
    price = (
        data.area_sqm * 15_000_000
        - data.distance_to_center_km * 5_000_000
        + data.bedrooms * 20_000_000
    )
    return HousePricePrediction(predicted_price=price)
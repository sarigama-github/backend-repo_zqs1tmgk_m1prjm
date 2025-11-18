import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import SparePart, Order

app = FastAPI(title="Car Spare Parts Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Car Spare Parts Shop API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.get("/api/spare-parts")
def list_spare_parts(q: Optional[str] = None, category: Optional[str] = None, brand: Optional[str] = None, limit: int = 50):
    """List spare parts with optional search and filters"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_query = {}
    if q:
        filter_query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"sku": {"$regex": q, "$options": "i"}},
            {"brand": {"$regex": q, "$options": "i"}},
            {"category": {"$regex": q, "$options": "i"}},
        ]
    if category:
        filter_query["category"] = category
    if brand:
        filter_query["brand"] = brand

    docs = get_documents("sparepart", filter_query, limit)
    # Convert ObjectId to str
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return {"items": docs}


@app.post("/api/spare-parts", status_code=201)
def create_spare_part(part: SparePart):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("sparepart", part)
    return {"id": inserted_id}


@app.get("/api/spare-parts/{part_id}")
def get_spare_part(part_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        doc = db["sparepart"].find_one({"_id": ObjectId(part_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")
        doc["_id"] = str(doc["_id"])  # type: ignore
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.post("/api/orders", status_code=201)
def create_order(order: Order):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    order_id = create_document("order", order)
    return {"id": order_id}


# Simple schema exposure for the viewer
@app.get("/schema")
def get_schema():
    from schemas import User, SparePart, Order, OrderItem  # noqa: F401
    return {
        "collections": [
            "user",
            "sparepart",
            "order"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

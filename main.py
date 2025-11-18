import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Listing, User

app = FastAPI(title="P2P Steam Skins API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateListingResponse(BaseModel):
    id: str
    message: str


@app.get("/")
def read_root():
    return {"message": "Steam Skins Marketplace API"}


@app.get("/api/listings")
def list_listings(
    game: Optional[str] = Query(None, description="Filter by game: CS2, Dota2, Rust, TF2"),
    q: Optional[str] = Query(None, description="Search by skin name"),
    limit: int = Query(24, ge=1, le=100)
):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_dict = {}
    if game:
        filter_dict["game"] = game
    if q:
        filter_dict["skin_name"] = {"$regex": q, "$options": "i"}

    docs = get_documents("listing", filter_dict, limit)

    # Convert ObjectId to str for _id
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}


@app.post("/api/listings", response_model=CreateListingResponse)
def create_listing(payload: Listing):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    new_id = create_document("listing", payload)
    return {"id": new_id, "message": "Listing created"}


@app.get("/api/featured")
def featured_listings(limit: int = 8):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    items = get_documents("listing", {"status": "active"}, limit)
    for d in items:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": items}


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

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


@app.get("/schema")
def get_schema():
    # Provide minimal schema info for viewers/tools
    return {
        "user": User.model_json_schema(),
        "listing": Listing.model_json_schema()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

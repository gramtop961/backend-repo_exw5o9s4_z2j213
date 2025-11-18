"""
Database Schemas for P2P Steam Skins Marketplace

Each Pydantic model represents a MongoDB collection.
Collection name = lowercase of class name (e.g., Listing -> "listing").
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal

# Users who trade/sell skins
class User(BaseModel):
    username: str = Field(..., description="Unique handle for the user")
    avatar_url: Optional[HttpUrl] = Field(None, description="Profile avatar")
    steam_id: Optional[str] = Field(None, description="Steam ID64")
    rating: float = Field(5.0, ge=0, le=5, description="Seller rating")
    is_verified: bool = Field(False, description="Whether the user is verified")

# Listings of individual skins
class Listing(BaseModel):
    skin_name: str = Field(..., description="Name of the skin/item")
    game: Literal["CS2", "Dota2", "Rust", "TF2"] = Field(..., description="Game category")
    price_usd: float = Field(..., ge=0, description="Listing price in USD")
    image_url: Optional[HttpUrl] = Field(None, description="Image of the skin")
    float_value: Optional[float] = Field(None, ge=0, le=1, description="Wear/float value if applicable (CS2)")
    rarity: Optional[str] = Field(None, description="Rarity tier e.g., Covert, Immortal, Legendary")
    seller_username: Optional[str] = Field(None, description="Seller username reference")
    instant_sell: bool = Field(False, description="Whether instant delivery is available")
    status: Literal["active", "sold", "inactive"] = Field("active", description="Listing status")

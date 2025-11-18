"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (you can keep these and add new ones below)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class SparePart(BaseModel):
    """
    Car spare parts collection schema
    Collection name: "sparepart"
    """
    name: str = Field(..., description="Part name")
    sku: str = Field(..., description="Stock keeping unit")
    brand: str = Field(..., description="Manufacturer/Brand")
    category: str = Field(..., description="Category, e.g., Brakes, Filters")
    price: float = Field(..., ge=0, description="Price in dollars")
    stock: int = Field(..., ge=0, description="Units in stock")
    compatibility: list[str] = Field(default_factory=list, description="Compatible car models")
    image_url: Optional[str] = Field(None, description="Image URL")
    description: Optional[str] = Field(None, description="Description")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced spare part id")
    name: str = Field(..., description="Product name snapshot")
    price: float = Field(..., ge=0, description="Unit price at purchase time")
    quantity: int = Field(..., ge=1, description="Quantity")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str
    email: EmailStr
    phone: str
    address: str
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    delivery_fee: float = Field(0, ge=0)
    total: float = Field(..., ge=0)

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!

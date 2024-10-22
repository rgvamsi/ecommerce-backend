from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Literal
from typing import Optional

class Product(BaseModel):
    name: str = Field(
        ..., min_length=3, max_length=50, 
        description="name must be between 3 and 50 characters."
    )
    description: str = Field(
        ..., min_length=3, max_length=50, 
        description="description must be between 3 and 50 characters."
    )
    price: float = Field(..., gt=0, description="Price must be a positive number")  # Use gt=0 for positive float
    stock: int = Field(..., ge=0, description="Stock must be a non-negative integer")
    stock_status: Literal["in stock", "not in stock"]
    image: str = Field(
        ..., min_length=5, max_length=200, 
        description="image link must be between 5 and 200 characters."
    ) #image link
    @model_validator(mode="after")  # This runs after all fields are validated
    def set_stock_status(cls, values):
        """Automatically set stock status based on the stock value."""
        if values.stock > 0:
            values.stock_status = "in stock"
        else:
            values.stock_status = "not in stock"
        return values

class ProductInDB(Product):
    id: str
    created_at: datetime
    updated_at: datetime

class ProductUpdateModel(BaseModel):
    name: Optional[str] = Field(
        ..., min_length=3, max_length=50, 
        description="name must be between 3 and 50 characters."
    )
    description: Optional[str] = Field(
        ..., min_length=3, max_length=50, 
        description="description must be between 3 and 50 characters."
    )
    price: Optional[float] = Field(..., gt=0, description="Price must be a positive number")  # Use gt=0 for positive float
    stock: Optional[int] = Field(..., ge=0, description="Stock must be a non-negative integer")
    stock_status: Optional[Literal["in stock", "not in stock"]]
    image: Optional[str] = Field(
        ..., min_length=5, max_length=200, 
        description="image link must be between 5 and 200 characters."
    ) #image link
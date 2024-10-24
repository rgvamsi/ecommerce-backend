from fastapi import FastAPI
from app.routes.users import router as users_router
from app.routes.products import router as product_router
from app.routes.cart import router as cart_router

app = FastAPI()

# Include the user and product routers
app.include_router(users_router, tags=["Users"])
app.include_router(product_router, tags=["Products"])
app.include_router(cart_router, tags=["Cart"])

# Optional root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the e-commerce API"}

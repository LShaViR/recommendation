from db.schema import ProductUpdate
from services.create_product import push_product_to_queue
from db.schema import get_session
from fastapi import Depends
from db.schema import ProductCreate
from contextlib import asynccontextmanager
from db.schema import create_db_and_tables
from typing import Union
from sqlmodel import Session
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: connecting to DB...")
    create_db_and_tables()
    yield
    print("Shutting down: closing DB connection...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/product/{product_id}")
def read_item(product_id: int, q: Union[str, None] = None):
    return {"product_id": product_id, "q": q}


@app.put("/product/{product_id}")
def update_item(product_id: int, product: ProductUpdate):
    return {"product_name": product.title, "product_id": product_id}


@app.post("/product")
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    push_product_to_queue(product)
    return {"product_name": product.title}


@app.post("/auth/login")
def login():
    return {"message": "Login successful"}


if __name__ == "__main__":
    import uvicorn

    # This triggers the FastAPI startup sequence
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

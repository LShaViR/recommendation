from db.schema import get_session
from db.schema import ProductCreate
from fastapi import Depends
from sqlmodel import Session

product_queue = []


def push_product_to_queue(product: ProductCreate):
    product_queue.append(product)


def create_item(product: ProductCreate, session: Session = Depends(get_session)):
    push_product_to_queue(product)
    return {"product_name": product.title}

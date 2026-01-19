from db.schema import get_session
from db.schema import ProductCreate
from fastapi import Depends

product_queue = []


def push_product_to_queue(product: ProductCreate):
    product_queue.append(product)

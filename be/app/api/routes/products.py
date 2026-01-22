import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Product,
    ProductCreate,
    ProductPublic,
    ProductsPublic,
    ProductUpdate,
    Message,
)
from app.service.queue_service import queue_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductsPublic)
def read_products(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve products.
    """

    count_statement = select(func.count()).select_from(Product)
    count = session.exec(count_statement).one()
    statement = select(Product).offset(skip).limit(limit)
    products = session.exec(statement).all()
    public_data = [ProductPublic.model_validate(p) for p in products]

    return ProductsPublic(data=public_data, count=count)


@router.get("/{id}", response_model=ProductPublic)
def read_product(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get product by ID.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductPublic)
async def create_product(
    *, session: SessionDep, current_user: CurrentUser, product_in: ProductCreate
) -> Any:
    product = Product.model_validate(
        product_in,
    )
    queued = await queue_service.queue_product(product_id=product.id)

    if not queued:
        raise HTTPException(status_code=500, detail="Queuing issue")

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@router.put("/{id}", response_model=ProductPublic)
def update_product(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    product_in: ProductUpdate,
) -> Any:
    """
    Update an product.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and (product.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = product_in.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_dict)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{id}")
def delete_product(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an product.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and (product.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")

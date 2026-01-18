from services.create_product import product_queue
from models.response import ErrorResponse
from typing import List, TypedDict, Union
from db.schema import ProductCreate
from db.schema import Product
from db.schema import get_session
from fastapi import Depends
from sqlmodel import Session
from gemini_embedding import gemini_embeddings


class ProductEmbeddings(TypedDict):
    occasion_embedding: List[float]
    style_embedding: List[float]
    color_embedding: List[float]
    overall_embedding: List[float]


def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    try:
        product_embeddings = create_embeddings(product)

        if "error" in product_embeddings:
            raise Exception(product_embeddings["error"])

        session.add(Product(**product.dict(), **product_embeddings))
        session.commit()

        return {"product_id": product.id, "product": product}
    except Exception as e:
        return {"error": str(e)}


def create_embeddings(
    product: ProductCreate,
) -> Union[ProductEmbeddings, ErrorResponse]:
    try:
        occasion_embedding = gemini_embeddings.embed_query(product.occasion)
        style_embedding = gemini_embeddings.embed_query(product.style)
        color_embedding = gemini_embeddings.embed_query(product.primary_color)
        overall_embedding = gemini_embeddings.embed_query(
            f"{product.title} {product.description} {product.sector} {product.brand_name} {product.product_type} {product.occasion} {product.season} {product.primary_color}"
        )
        return {
            "occasion_embedding": occasion_embedding,
            "style_embedding": style_embedding,
            "color_embedding": color_embedding,
            "overall_embedding": overall_embedding,
        }

    except Exception as e:
        return {"error": str(e)}


while True:
    product = product_queue.pop(0)
    create_product(product)

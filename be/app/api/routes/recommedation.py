import uuid
from fastapi import APIRouter, HTTPException

from sqlmodel import Session, select, and_
from sentence_transformers import util

from app.api.deps import SessionDep, CurrentUser
from app.models import PersonalizedOutfits, Product, ProductCompatibility, User

router = APIRouter(prefix="/recommendation", tags=["/recommendation"])
USER_WEIGHTS = {
    "compatibility": 0.40,
    "price_match": 0.30,
    "style_alignment": 0.30,
}


def calculate_price_score(user: User, product: Product) -> float:
    """Matches product price against User's spending_dna and price_sensitivity."""
    category = product.sub_category.lower()
    user_dna = user.spending_profile.get(category, {})

    avg_spent = user_dna.get("avg", 0)
    max_spent = user_dna.get("max", 0)

    if not avg_spent:
        return 0.5

    if product.price <= avg_spent:
        return 1.0
    elif product.price <= max_spent:
        ratio = (product.price - avg_spent) / (max_spent - avg_spent + 1e-6)
        return 1.0 - (ratio * user.price_sensitivity_score)
    else:
        return 0.1


def generate_personalized_outfits(session: Session, user: User, base_product: Product):
    """
    1. Retrieval: Fetch pre-computed items from the Graph.
    2. Re-rank: Apply User DNA.
    3. Outfit Construction: Assemble Top/Bottom/Shoe/Acc sets.
    """

    statement = (
        select(Product, ProductCompatibility.compatibility_score)
        .join(
            ProductCompatibility,
            and_(Product.id == ProductCompatibility.recommended_product_id),
        )
        .where(ProductCompatibility.base_product_id == base_product.id)
    )
    results = session.exec(statement).all()
    scored_items = []

    for candidate, comp_score in results:
        p_score = calculate_price_score(user, candidate)
        if not user.style_embedding or not candidate.style_embedding:
            u_style_score = 0.6
        else:
            u_style_score = util.cos_sim(
                user.style_embedding, candidate.style_embedding
            ).item()

        final_rank_score = (
            (comp_score * USER_WEIGHTS["compatibility"])
            + (p_score * USER_WEIGHTS["price_match"])
            + (u_style_score * USER_WEIGHTS["style_alignment"])
        )

        scored_items.append({"product": candidate, "score": final_rank_score})

    scored_items.sort(key=lambda x: x["score"], reverse=True)
    outfits = []

    for i in range(5):
        try:
            outfit = {
                "base": base_product,
                "bottom": next(
                    item["product"]
                    for item in scored_items
                    if item["product"].sub_category == "Bottomwear"
                ),
                "shoe": next(
                    item["product"]
                    for item in scored_items
                    if item["product"].sub_category == "Shoes"
                ),
                "accessory": next(
                    item["product"]
                    for item in scored_items
                    if item["product"].sub_category == "Accessories"
                ),
            }
            scored_items = [
                item
                for item in scored_items
                if item["product"].id
                not in [outfit["bottom"].id, outfit["shoe"].id, outfit["accessory"].id]
            ]
            outfits.append(outfit)
        except StopIteration:
            break

    return outfits


@router.get("/{product_id}", response_model=PersonalizedOutfits)
def get_personalized_outfits_route(
    product_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Fetch the base product, then retrieve and re-rank compatible items
    to build 5 personalized outfits based on the user's DNA.
    """
    print(current_user)

    base_product = session.get(Product, product_id)
    if not base_product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        recommendations = generate_personalized_outfits(
            session=session, user=current_user, base_product=base_product
        )
    except Exception as e:
        print(f"Error generating outfits: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not generate recommendations at this time.",
        )

    if not recommendations:
        return {"outfits": []}

    return {"outfits": recommendations}

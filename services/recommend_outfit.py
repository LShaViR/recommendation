from db.schema import Color
from constants.product_type import product_type_array
from constants.color_map import stylist_color_dict
from db.schema import get_session
from db.schema import Product
from fastapi import Depends, HTTPException
from sqlmodel import Session, select, and_, func, case
from sqlalchemy import desc
from db.schema import User


def get_current_user(token: str, session: Session = Depends(get_session)) -> User:
    user_id = "first_user_id"
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def recommend_outfit(
    product_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    base_product = session.get(Product, product_id)
    if not base_product:
        raise HTTPException(status_code=404, detail="Product not found")

    outfit = {}
    categories = [
        product_type
        for product_type in product_type_array
        if product_type != base_product.product_type
    ]

    allowed_colors = stylist_color_dict.get(base_product.primary_color, [])

    colors = session.exec(select(Color).where(Color.name.in_(allowed_colors))).all()

    color_sims = [
        (1 - Product.color_vector.cosine_distance(color.vector)) for color in colors
    ]

    color_score = 0.20 * func.greatest(*color_sims)

    occ_score = 0.25 * (
        1 - Product.occasion_vector.cosine_distance(base_product.occasion_vector)
    )

    style_score = 0.35 * (
        1 - Product.style_vector.cosine_distance(base_product.style_vector)
    )

    season_score = 0.10 * case((Product.season == base_product.season, 1), else_=0)

    overall_score = 1 - Product.overall_vector.cosine_distance(
        base_product.overall_vector
    )

    total_score = (
        0.7 * (color_score + occ_score + style_score + season_score)
        + 0.3 * 0.9 * overall_score
    )

    for cat in categories:
        statement = (
            select(Product, total_score.label("compatibility_score"))
            .where(
                and_(
                    Product.product_type == cat,
                    Product.primary_color.in_(allowed_colors),
                    Product.occasion == base_product.occasion,
                    Product.season == base_product.season,
                )
            )
            .order_by(desc("compatibility_score"))
            .limit(1)
        )

        match = session.exec(statement).first()

        if not match:
            statement = (
                select(Product, total_score.label("compatibility_score"))
                .where(Product.product_type == cat)
                .order_by(desc("compatibility_score"))
                .limit(1)
            )
            match = session.exec(statement).first()

        outfit[cat] = match

    outfit_score = sum([match.compatibility_score for match in outfit.values()]) * 90

    total_price = sum([match.price for match in outfit.values()]) + base_product.price

    if total_price <= user.budget:
        outfit_score += 10
    elif total_price <= user.budget * 1.2:
        outfit_score += 5
    elif total_price <= user.budget * 1.5:
        outfit_score += 2
    elif total_price <= user.budget * 2:
        outfit_score += 1

    return {
        "base_product": base_product.title,
        "outfit": outfit,
        "outfit_score": outfit_score,
        "total_price": total_price,
    }

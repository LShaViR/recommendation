from sqlmodel import Session, func, select
from app.models import Product, ProductCompatibility
from app.worker.utils.config_model import CATEGORY_MAP, FIT_COMPATIBILITY
from sentence_transformers import util
from collections import defaultdict

# --- STYLIST WEIGHTING CONFIGURATION ---
# Higher values = more influence on the final recommendation
WEIGHTS = {
    "season": 0.35,  # Highest: Season misalignment is a dealbreaker
    "occasion": 0.25,  # High: Occasion context matters
    "style_vibe": 0.20,  # Medium: Aesthetic (Vector similarity)
    "fit": 0.15,  # Lower: Structural compatibility
    "color": 0.05,  # Bonus: Harmony
}


def get_season_score(p1_season: str | None, p2_season: str | None) -> float:
    if not p1_season or not p2_season:
        return 0.5
    if p1_season == p2_season:
        return 1.0
    # Allow transitional matching (e.g., Spring & Summer)
    transitional = {
        ("Spring", "Summer"),
        ("Autumn", "Winter"),
        ("All Season", "Summer"),
    }
    if (p1_season, p2_season) in transitional or (p2_season, p1_season) in transitional:
        return 0.7
    return 0.2  # Penalty for Winter vs Summer


def get_occasion_score(p1_tags: list[str], p2_tags: list[str]) -> float:
    # Jaccard Similarity: Intersection / Union
    set1, set2 = set(p1_tags), set(p2_tags)
    intersection = set1.intersection(set2)
    if not intersection:
        return 0.1
    return len(intersection) / len(set1.union(set2))


async def precompute_fuzzy_compatibility(session: Session, new_product: Product):
    print("precompute start")
    current_sub = (new_product.sub_category or "").lower()
    target_categories = [c.lower() for c in CATEGORY_MAP.get(current_sub, [])]

    print(target_categories)
    if not target_categories:
        print(f"No target categories mapped for: {current_sub}")
        return []

    statement_1 = (
        select(Product)
        .where(
            Product.id != new_product.id,
            func.lower(Product.sub_category) == (target_categories[0]),
        )
        .limit(500)
    )

    statement_2 = (
        select(Product)
        .where(
            Product.id != new_product.id,
            func.lower(Product.sub_category) == (target_categories[1]),
        )
        .limit(300)
    )

    statement_3 = (
        select(Product)
        .where(
            Product.id != new_product.id,
            func.lower(Product.sub_category) == (target_categories[2]),
        )
        .limit(200)
    )

    candidates = (
        session.exec(statement_1).all()
        + session.exec(statement_2).all()
        + session.exec(statement_3).all()
    )

    scored_candidates = []

    for cand in candidates:
        # A. Season Score (Soft)
        s_score = get_season_score(new_product.season, cand.season)

        # B. Occasion Score (Soft)
        o_score = get_occasion_score(
            new_product.occasion_tags, cand.occasion_tags)

        if new_product.complementary_embedding is None or cand.style_embedding is None:
            print(
                f"Skipping compatibility check: One vector is None",
                new_product.complementary_embedding,
                cand.style_embedding,
            )
            continue

        # C. Style/Vibe (Vector Similarity)
        v_score = util.cos_sim(
            new_product.complementary_embedding, cand.style_embedding
        ).item()

        # D. Fit (Stylist Rule)
        f_score = FIT_COMPATIBILITY.get((new_product.fit, cand.fit), 0.5)

        # FINAL WEIGHTED SUM
        final_score = (
            (s_score * WEIGHTS["season"])
            + (o_score * WEIGHTS["occasion"])
            + (v_score * WEIGHTS["style_vibe"])
            + (f_score * WEIGHTS["fit"])
        )

        scored_candidates.append((cand, final_score))

    category_groups = defaultdict(list)
    for cand, score in scored_candidates:
        # Assuming 'cand' has a .category attribute
        category_groups[cand.sub_category].append((cand, score))

    # 2. Sort each category group by score descending
    for cat in category_groups:
        category_groups[cat].sort(key=lambda x: x[1], reverse=True)

    # 3. Diverse Selection (Round-Robin)
    top_matches = []
    limit = 40
    categories = list(category_groups.keys())

    # We loop through the ranks (0, 1, 2...) and pick one from each category
    rank_idx = 0
    while len(top_matches) < limit and categories:
        for cat in list(categories):  # Use list() to allow removal during iteration
            if rank_idx < len(category_groups[cat]):
                top_matches.append(category_groups[cat][rank_idx])

                # Stop immediately if we hit our global limit
                if len(top_matches) >= limit:
                    break
            else:
                # No more items in this category, stop checking it
                categories.remove(cat)
        rank_idx += 1  # 2. Sort by Score and Pick Top 40

    # 3. Store in DB
    links = [
        ProductCompatibility(
            base_product_id=new_product.id,
            recommended_product_id=item.id,
            compatibility_score=score,
            occasion_context=new_product.occasion_tags[0]
            if new_product.occasion_tags
            else "General",
        )
        for item, score in top_matches
    ]

    session.add_all(links)
    session.commit()

from io import BytesIO
from app.core.config import settings
from app.models import Product
from app.worker.utils.config_model import Image, vision_model, text_model
import torch.nn.functional as F
import httpx

OCCASIONS = [
    "Wedding",
    "Office",
    "Gym/Workout",
    "Casual/Daily",
    "Party/Nightlife",
    "Beach/Vacation",
]
ARCHETYPES = [
    "Minimalist",
    "Streetwear",
    "Bohemian",
    "Preppy",
    "Vintage",
    "Classic/Elegant",
]

# Formality Anchors (used to calculate the 0-1 score)
FORMALITY_LABELS = ["Extremely Casual Streetwear", "Very Formal Black Tie"]

VULTR_REGION = settings.VULTR_REGION  # e.g., ewr1, sgp1, ams1
VULTR_ENDPOINT = f"https://{VULTR_REGION}.vultrobjects.com"


async def load_image_from_url(url: str) -> Image.Image:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download image from {url}")

        # Wrap the bytes in a BytesIO object so Pillow can read it
        return Image.open(BytesIO(response.content))


async def compute_product_signals(product: Product) -> Product:
    """
    Computes visual and textual embeddings + extracts tags.
    """
    # A. Visual Embedding (The 'Style' DNA)
    image_path = product.images[0]

    if not image_path:
        raise Exception("image path not exist")

    formatted_image_url = f"{VULTR_ENDPOINT}/{image_path}"

    try:
        img = await load_image_from_url(formatted_image_url)
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    img_features = vision_model.encode(img, convert_to_tensor=True)
    product.style_embedding = img_features.tolist()

    product.complementary_embedding = product.style_embedding

    occasion_queries = [f"A photo of clothing for a {o}" for o in OCCASIONS]

    text_features = vision_model.encode(
        occasion_queries, convert_to_tensor=True)

    probs = (img_features @ text_features.T).softmax(dim=-1)

    product.occasion_tags = [
        OCCASIONS[i] for i, score in enumerate(probs) if score > 0.20
    ]

    archetype_queries = [f"clothing in {a} style" for a in ARCHETYPES]
    archetype_features = vision_model.encode(
        archetype_queries, convert_to_tensor=True)

    archetype_probs = (img_features @ archetype_features.T).softmax(dim=-1)
    product.style_archetype = ARCHETYPES[archetype_probs.argmax()]

    formality_queries = [f"a photo of {f}" for f in FORMALITY_LABELS]
    f_features = vision_model.encode(formality_queries, convert_to_tensor=True)

    f_probs = (img_features @ f_features.T).softmax(dim=-1)
    product.formality_score = float(f_probs[1])

    text_desc = (
        f"Product Name: {product.name}. "
        f"Brand: {product.brand}. "
        f"Category: {product.gender} {product.master_category} - {
            product.sub_category
        } ({product.article_type}). "
        f"Color: {product.primary_colour}. "
        f"Season: {product.season}. "
        f"Style: This is a {product.primary_colour} {
            product.article_type
        } with a formality score of {product.formality_score}."
    )
    product.semantic_embedding = text_model.encode(text_desc).tolist()

    return product

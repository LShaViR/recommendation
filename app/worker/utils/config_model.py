import torch
from PIL import Image
from sentence_transformers import SentenceTransformer, util
from sqlmodel import Session, select, col

# Load models once (Global)
# CLIP: Handles visual aesthetic and colors
vision_model = SentenceTransformer("clip-ViT-B-32")
# Text: Handles semantic search (e.g., "winter wedding")
text_model = SentenceTransformer("all-MiniLM-L6-v2")

# Stylist Rule Constants
CATEGORY_MAP = {
    "topwear": ["bottomwear", "shoes", "accessories"],
    "bottomwear": ["topwear", "shoes", "accessories"],
    "shoes": ["bottomwear", "topwear", "accessories"],
    "accessories": ["topwear", "bottomwear", "shoes"],
}

FIT_COMPATIBILITY = {
    ("slim", "oversized"): 1.2,  # bonus for contrast
    ("regular", "regular"): 1.0,
    ("oversized", "oversized"): 0.8,  # often too baggy
}

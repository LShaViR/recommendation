import torch
from PIL import Image
from sentence_transformers import SentenceTransformer, util

vision_model = SentenceTransformer("clip-ViT-B-32")
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

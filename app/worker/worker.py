import asyncio
from arq.connections import RedisSettings
from sqlmodel import Session, select
from app.core.db import engine  # Import your SQLModel engine
from app.models import Product  # Import your Product model
import os

from app.worker.functions.compute_product import compute_product_signals
from app.worker.functions.precompute_compatibility_match import (
    precompute_fuzzy_compatibility,
)
import time


# 1. The Task Function
async def process_product(ctx, product_id: str):
    """
    This function runs in the background.
    'ctx' is a dictionary containing the redis connection and other metadata.
    """
    print(f"--- Starting background task for product: {product_id} ---")

    # Example logic: Fetch from DB and do something (e.g., generate embeddings)
    with Session(engine) as session:
        statement = select(Product).where(True).limit(10000)
        products = session.exec(statement).all()
        for prod in products:
            await precompute_fuzzy_compatibility(session, prod)

        product = session.get(Product, product_id)
        if not product or product:
            print(f"Product {product_id} not found in DB yet. Retrying...")
            return

        product = await compute_product_signals(product)
        session.add(product)
        session.commit()

        # 2. Build the Compatibility Graph (Step 3)
        # This compares the new item against the existing catalog
        await precompute_fuzzy_compatibility(session, product)

        time.sleep(1)
        # Simulate work (e.g., calling an AI API for embeddings)
        print(f"Product {product.id} processed successfully!")


# 2. Worker Configuration
class WorkerSettings:
    # Point to your Redis container (using the service name from docker-compose)
    redis_settings = RedisSettings(host=os.getenv(
        "REDIS_HOST", "localhost"), port=6379)

    # List of functions the worker is allowed to execute
    functions = [process_product]

    # Optional: Logic to run when the worker starts
    async def on_startup(ctx):
        print("Worker starting up...")

    async def on_shutdown(ctx):
        print("Worker shutting down...")

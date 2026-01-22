from uuid import UUID
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
import os

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")


class StyleQueueService:
    def __init__(self):
        self.pool: ArqRedis | None = None
        self.redis_settings = RedisSettings(host=REDIS_HOST, port=6379)

    async def get_redis(self) -> ArqRedis:
        """Ensures the pool is always ready before use."""
        if self.pool is None:
            self.pool = await create_pool(self.redis_settings)
        return self.pool

    async def queue_product(self, product_id: UUID):
        redis = await self.get_redis()
        return await redis.enqueue_job("process_product", product_id)


queue_service = StyleQueueService()

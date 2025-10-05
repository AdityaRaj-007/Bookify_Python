import aioredis
from src.config import Config

TOKEN_EXPIRY = 3600

blocklisted_token = aioredis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0
)

async def add_token_to_blocklist(jti: str) -> None:
    await blocklisted_token.set(
        name=jti,
        value="",
        ex=TOKEN_EXPIRY
    )

async def token_in_blocklist(jti:str) -> bool:
    jti = await blocklisted_token.get(jti)

    return jti is not None
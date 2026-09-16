from fastapi import Request, HTTPException, Depends
from ..dependencies import RedisDependency


def rate_limit(limit: int, seconds: int = 60):
    async def dependency(request: Request, redis: RedisDependency):
        client_ip = request.client.host if request.client else "unknown"
        limit_key = f"rate_limit:{client_ip}:{request.url.path}"

        current_requests = await redis.incr(limit_key)

        if current_requests == 1:
            await redis.expire(limit_key, seconds)

        if current_requests > limit:
            raise HTTPException(
                status_code=429, detail={"message": "Rate limit exceeded"}
            )

    return Depends(dependency)

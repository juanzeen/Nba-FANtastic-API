from fastapi import FastAPI, Depends, HTTPException
from .dependencies import get_client
from .routers import historical_players, historical_records, nba_players

app = FastAPI()

app.include_router(historical_players.router)
app.include_router(historical_records.router)
app.include_router(nba_players.router)


@app.get("/", status_code=200, tags=["App"])
async def health_check(client=Depends(get_client)):
    health_status = {
        "status": "healthy",
        "services": {"api": "healthy", "database": "unknown"},
    }

    try:
        ping = await client.admin.command("ping")
        if ping:
            health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["services"]["error"] = str(e)
        health_status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

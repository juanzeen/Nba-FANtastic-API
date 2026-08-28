from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_db

router = APIRouter(prefix="/players")

@router.get("/", status_code=200)
async def get_nba_players(db=Depends(get_db)):
  np = db["players"]
  players = await np.find().to_list()
  if players and len(players) > 0:
    print(players)
    return {"message": "Actual NBA players successfully retrieved.", "data": players}
  raise HTTPException(status_code=404, detail={"message": "Actual NBA players not found."})

@router.get("/{id}", status_code=200)
async def get_nba_player_by_id(id: int, db=Depends(get_db)):
  np = db["players"]
  player = await np.find_one({"_id": id})
  if player:
    return {"message": "Player successfully retrieved.", "data": player}
  raise HTTPException(status_code=404, detail={"message": f"Player with id: {id} not found."})

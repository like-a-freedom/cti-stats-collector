from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from . import storage
from models import RankModel, FeedStatsModel
from fastapi import FastAPI, Response, status, HTTPException

api = FastAPI()


@api.post("/insert_stats")
async def insert_stats(stats: FeedStatsModel, response: Response):
    if storage.write_stats(stats) == 1:
        response.status_code = status.HTTP_200_OK
        return {"message": "Stats inserted"}
    else:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown error"
        )


@api.post("/insert_ranks")
async def insert_ranks():
    pass

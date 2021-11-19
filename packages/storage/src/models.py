from typing import List
from pydantic import BaseModel


class StatsModel(BaseModel):
    feed_name: str
    dt: date
    is_updated: int


class RankModel(BaseModel):
    feed_name: str
    dt: str
    extensivess: int
    timeliness: int
    completeness: int
    wl_overlap: int
    source_confidence: int


class FeedStatsModel(BaseModel):
    stats: List[StatsModel]

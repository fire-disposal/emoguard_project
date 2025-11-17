from ninja import Schema
from typing import List

class EmotionRecordCreateSchema(Schema):
    depression: int
    anxiety: int
    energy: int
    sleep: int

class EmotionRecordResponseSchema(Schema):
    id: int
    user_id: str
    depression: int
    anxiety: int
    energy: int
    sleep: int
    created_at: str

class EmotionTrendSchema(Schema):
    dates: List[str]
    depression: List[int]
    anxiety: List[int]
    energy: List[int]
    sleep: List[int]
from ninja import Schema
from typing import List

class EmotionRecordCreateSchema(Schema):
    depression: int
    anxiety: int
    energy: int
    sleep: int
    mainMood: str = None
    moodIntensity: int = None
    mainMoodOther: str = None
    moodSupplementTags: list = None
    moodSupplementText: str = None
    period: str = None
    device_info: dict = None

class EmotionRecordResponseSchema(Schema):
    id: int
    user_id: str
    depression: int
    anxiety: int
    energy: int
    sleep: int
    mainMood: str = None
    moodIntensity: int = None
    mainMoodOther: str = None
    moodSupplementTags: list = None
    moodSupplementText: str = None
    period: str = None
    device_info: dict = None
    created_at: str

class EmotionTrendSchema(Schema):
    dates: List[str]
    depression: List[int]
    anxiety: List[int]
    energy: List[int]
    sleep: List[int]
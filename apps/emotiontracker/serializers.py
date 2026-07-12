from ninja import Schema, Field
from typing import List, Optional

class EmotionRecordCreateSchema(Schema):
    depression: int = Field(ge=0, le=100)
    anxiety: int = Field(ge=0, le=100)
    energy: int = Field(ge=0, le=100)
    sleep: int = Field(ge=0, le=100)
    mainMood: Optional[str] = None
    moodIntensity: Optional[int] = Field(default=None, ge=0, le=100)
    mainMoodOther: Optional[str] = None
    moodSupplementTags: Optional[list] = None
    moodSupplementText: Optional[str] = None

class EmotionRecordResponseSchema(Schema):
    id: int
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
    started_at: str = None

class EmotionTrendSchema(Schema):
    dates: List[str]
    depression: List[int]
    anxiety: List[int]
    energy: List[int]
    sleep: List[int]
from ninja import Schema
from typing import Optional

class MoodJournalCreateSchema(Schema):
    mainMood: str = ""
    moodIntensity: int = 0
    mainMoodOther: str = ""
    moodSupplementTags: dict = None
    moodSupplementText: str = ""

class MoodJournalUpdateSchema(Schema):
    mainMood: Optional[str] = None
    moodIntensity: Optional[int] = None
    mainMoodOther: Optional[str] = None
    moodSupplementTags: Optional[dict] = None
    moodSupplementText: Optional[str] = None

class MoodJournalResponseSchema(Schema):
    id: int
    mainMood: str
    moodIntensity: int
    mainMoodOther: str
    moodSupplementTags: dict
    moodSupplementText: str
    record_date: str
    created_at: str

class MoodJournalListQuerySchema(Schema):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    mainMood: Optional[str] = None
    page: int = 1
    page_size: int = 10

class MoodStatisticsSchema(Schema):
    date: str
    avg_score: float
    mood_count: int
    dominant_mood: str
from ninja import Schema
from typing import Optional

class MoodJournalCreateSchema(Schema):
    mood_score: int
    mood_name: str
    mood_emoji: str
    text: str
    record_date: Optional[str] = None

class MoodJournalUpdateSchema(Schema):
    mood_score: Optional[int] = None
    mood_name: Optional[str] = None
    mood_emoji: Optional[str] = None
    text: Optional[str] = None
    record_date: Optional[str] = None

class MoodJournalResponseSchema(Schema):
    id: int
    user_id: str
    mood_score: int
    mood_name: str
    mood_emoji: str
    text: str
    record_date: str
    created_at: str
    updated_at: str

class MoodJournalListQuerySchema(Schema):
    user_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    mood_name: Optional[str] = None
    page: int = 1
    page_size: int = 10

class MoodStatisticsSchema(Schema):
    date: str
    avg_score: float
    mood_count: int
    dominant_mood: str
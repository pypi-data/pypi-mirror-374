from typing import List, Optional

from pydantic import BaseModel


class TextAnalysis(BaseModel):
    id: Optional[str] = None
    detected_languages: Optional[List[str]] = None
    key_phrases: Optional[List[str]] = None
    top_topics: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    resolution_score: Optional[float] = None

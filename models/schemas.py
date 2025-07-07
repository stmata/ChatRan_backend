from pydantic import BaseModel
from typing import List, Optional

class MessageItem(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    question: str
    language: Optional[str] = "en"
    allowed_topics: Optional[List[str]] = None 
    conversation_history: Optional[List[MessageItem]] = []

class ChatResponse(BaseModel):
    original_question: str
    sub_queries: List[str]
    response: str
    citations: List[str]
    out_of_scope: bool = False
    allowed_topics: Optional[List[str]] = None

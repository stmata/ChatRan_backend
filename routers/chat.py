from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.chat_service import handle_chat_gptweb

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/stream", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        print(request.conversation_history)
        resp = await handle_chat_gptweb(
            question=request.question,
            language=request.language,
            allowed_topics=request.allowed_topics,
            conversation_history=request.conversation_history
        )
        print(resp)
        return resp
    except Exception as e:
        print(f"ERROR in chat_stream_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

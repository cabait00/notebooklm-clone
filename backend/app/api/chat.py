from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, Source
from app.services import rag
from app.services.rag import LLMUnavailableError

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = rag.answer_question(request.question)
    except LLMUnavailableError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The answer generation service is currently unavailable. "
                "Please check the API key or try again later."
            ),
        )
    return ChatResponse(
        answer=result.answer,
        sources=[Source(**vars(s)) for s in result.sources],
        refused=result.refused,
    )

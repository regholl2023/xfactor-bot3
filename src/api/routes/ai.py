"""
API routes for AI assistant functionality.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.ai.assistant import get_ai_assistant
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


# =========================================================================
# Request/Response Models
# =========================================================================

class ChatRequest(BaseModel):
    """Chat request payload."""
    
    query: str
    session_id: Optional[str] = "default"
    include_context: bool = True


class ChatResponse(BaseModel):
    """Chat response payload."""
    
    response: str
    session_id: str


class InsightsResponse(BaseModel):
    """Quick insights response."""
    
    insights: list[str]


class OptimizationResponse(BaseModel):
    """Optimization analysis response."""
    
    timestamp: str
    summary: dict
    recommendations: list[dict]
    warnings: list[dict]
    opportunities: list[dict]
    context_snapshot: dict


# =========================================================================
# Routes
# =========================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Send a message to the AI assistant.
    
    The assistant has access to real-time system context including:
    - Portfolio positions and P&L
    - Strategy performance
    - Data source status
    - Bot activity
    - Risk metrics
    
    Example queries:
    - "How is my portfolio performing today?"
    - "Which strategy is generating the best returns?"
    - "What optimizations would you recommend?"
    """
    try:
        assistant = get_ai_assistant()
        
        response = await assistant.chat(
            query=request.query,
            session_id=request.session_id,
            include_context=request.include_context,
        )
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", response_model=InsightsResponse)
async def get_quick_insights():
    """
    Get quick insights about current system state.
    
    Returns a list of key observations about:
    - Portfolio performance
    - Position status
    - Bot activity
    - Risk alerts
    - Data source status
    """
    try:
        assistant = get_ai_assistant()
        insights = await assistant.get_quick_insights()
        
        return InsightsResponse(insights=insights)
        
    except Exception as e:
        logger.error(f"Insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimize")
async def get_optimization_recommendations():
    """
    Get AI-powered optimization recommendations.
    
    Analyzes current system state and provides:
    - Strategy optimization suggestions
    - Risk management recommendations
    - Data source improvements
    - Position sizing adjustments
    """
    try:
        assistant = get_ai_assistant()
        analysis = await assistant.analyze_for_optimization()
        
        return analysis
        
    except Exception as e:
        logger.error(f"Optimization analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples")
async def get_example_questions():
    """
    Get list of example questions to ask the AI assistant.
    """
    assistant = get_ai_assistant()
    return {"examples": assistant.get_example_questions()}


@router.post("/clear/{session_id}")
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a session.
    """
    try:
        assistant = get_ai_assistant()
        assistant.clear_conversation(session_id)
        
        return {"message": f"Conversation history cleared for session: {session_id}"}
        
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context")
async def get_system_context():
    """
    Get current system context used by the AI assistant.
    
    Returns the full context object that the AI uses to answer questions.
    Useful for debugging and understanding what data the AI sees.
    """
    try:
        from src.ai.context_builder import get_context_builder
        
        builder = get_context_builder()
        context = await builder.build_context()
        
        return context.model_dump()
        
    except Exception as e:
        logger.error(f"Context retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Optional

from app.config import settings
from app.models import (
    ChatRequest, 
    ChatResponse, 
    ConversationSummary, 
    AgentStatus, 
    ErrorResponse
)
from app.agent import agent

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Agent API built with FastAPI supporting multiple AI providers",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else "An unexpected error occurred"
        ).dict()
    )

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=AgentStatus)
async def health_check():
    """Health check endpoint"""
    return AgentStatus(
        status="healthy",
        version=settings.app_version,
        available_models=agent.get_available_models(),
        active_conversations=len(agent.conversation_manager.get_conversation_ids())
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for interacting with the AI agent"""
    try:
        result = await agent.process_message(
            user_message=request.message,
            conversation_id=request.conversation_id,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt
        )
        
        return ChatResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@app.get("/conversations", response_model=List[str])
async def get_conversations():
    """Get list of all active conversation IDs"""
    return agent.conversation_manager.get_conversation_ids()

@app.get("/conversations/{conversation_id}", response_model=ConversationSummary)
async def get_conversation_summary(conversation_id: str):
    """Get summary of a specific conversation"""
    summary = agent.get_conversation_summary(conversation_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationSummary(**summary)

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id not in agent.conversation_manager.conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    del agent.conversation_manager.conversations[conversation_id]
    return {"message": f"Conversation {conversation_id} deleted successfully"}

@app.get("/models", response_model=List[str])
async def get_available_models():
    """Get list of available AI models"""
    models = agent.get_available_models()
    if not models:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No AI providers configured. Please set API keys in environment variables."
        )
    return models

@app.post("/conversations/{conversation_id}/clear")
async def clear_conversation(conversation_id: str):
    """Clear all messages from a conversation"""
    if conversation_id not in agent.conversation_manager.conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    agent.conversation_manager.conversations[conversation_id] = []
    return {"message": f"Conversation {conversation_id} cleared successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

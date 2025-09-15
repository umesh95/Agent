from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    PERPLEXITY = "perplexity"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message to the AI agent")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    model: Optional[str] = Field(None, description="AI model to use (overrides default)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens in response")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI agent's response")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    model_used: str = Field(..., description="The AI model that generated the response")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")

class ConversationSummary(BaseModel):
    conversation_id: str
    message_count: int
    first_message: str
    last_message: str
    created_at: str
    updated_at: str

class AgentStatus(BaseModel):
    status: str = "healthy"
    version: str
    available_models: List[str]
    active_conversations: int

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None

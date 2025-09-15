import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import openai
import anthropic
from app.config import settings
from app.models import Message, MessageRole, AIProvider

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, List[Message]] = {}
    
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id: str, message: Message):
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message.timestamp = datetime.now().isoformat()
        self.conversations[conversation_id].append(message)
        
        # Keep conversation length manageable
        if len(self.conversations[conversation_id]) > settings.max_conversation_length:
            # Remove oldest messages but keep system message if present
            messages = self.conversations[conversation_id]
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            recent_messages = messages[-(settings.max_conversation_length - len(system_messages)):]
            self.conversations[conversation_id] = system_messages + recent_messages
    
    def get_conversation(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation"""
        return self.conversations.get(conversation_id, [])
    
    def get_conversation_ids(self) -> List[str]:
        """Get all active conversation IDs"""
        return list(self.conversations.keys())

class AIAgent:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.openai_client = None
        self.anthropic_client = None
        self.perplexity_client = None
        
        # Initialize AI clients
        if settings.openai_api_key and not settings.openai_api_key.startswith("pplx-"):
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        
        # Initialize Perplexity client (uses OpenAI-compatible API)
        if settings.perplexity_api_key or (settings.openai_api_key and settings.openai_api_key.startswith("pplx-")):
            api_key = settings.perplexity_api_key or settings.openai_api_key
            self.perplexity_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
    
    def _determine_provider(self, model: str) -> AIProvider:
        """Determine which AI provider to use based on model name"""
        if model.startswith("gpt") or model.startswith("text-"):
            return AIProvider.OPENAI
        elif model.startswith("claude"):
            return AIProvider.ANTHROPIC
        elif model.startswith("sonar") or model.startswith("llama") or model.startswith("mistral") or model.startswith("codellama"):
            return AIProvider.PERPLEXITY
        else:
            # Default to Perplexity for unknown models since we have that API key
            return AIProvider.PERPLEXITY
    
    async def _call_openai(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Make API call to OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def _call_anthropic(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Make API call to Anthropic"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        # Convert messages format for Anthropic
        system_message = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(msg)
        
        response = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else "You are a helpful AI assistant.",
            messages=anthropic_messages
        )
        
        return {
            "content": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }
    
    async def _call_perplexity(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Make API call to Perplexity"""
        if not self.perplexity_client:
            raise ValueError("Perplexity API key not configured")
        
        response = await self.perplexity_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }
    
    async def process_message(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message and return AI response"""
        
        # Use defaults if not provided
        model = model or settings.default_model
        temperature = temperature or settings.default_temperature
        max_tokens = max_tokens or settings.max_tokens
        
        # Create or get conversation
        if not conversation_id:
            conversation_id = self.conversation_manager.create_conversation()
        
        # Add system prompt if provided and conversation is new
        conversation = self.conversation_manager.get_conversation(conversation_id)
        if system_prompt and not conversation:
            system_message = Message(role=MessageRole.SYSTEM, content=system_prompt)
            self.conversation_manager.add_message(conversation_id, system_message)
        
        # Add user message
        user_msg = Message(role=MessageRole.USER, content=user_message)
        self.conversation_manager.add_message(conversation_id, user_msg)
        
        # Prepare messages for AI API
        conversation = self.conversation_manager.get_conversation(conversation_id)
        messages = [{"role": msg.role.value, "content": msg.content} for msg in conversation]
        
        # Determine provider and make API call
        provider = self._determine_provider(model)
        
        try:
            if provider == AIProvider.OPENAI:
                result = await self._call_openai(messages, model, temperature, max_tokens)
            elif provider == AIProvider.ANTHROPIC:
                result = await self._call_anthropic(messages, model, temperature, max_tokens)
            else:  # PERPLEXITY
                result = await self._call_perplexity(messages, model, temperature, max_tokens)
            
            # Add AI response to conversation
            assistant_msg = Message(role=MessageRole.ASSISTANT, content=result["content"])
            self.conversation_manager.add_message(conversation_id, assistant_msg)
            
            return {
                "response": result["content"],
                "conversation_id": conversation_id,
                "model_used": model,
                "usage": result["usage"]
            }
            
        except Exception as e:
            raise Exception(f"Error processing message with {provider.value}: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models based on configured API keys"""
        models = []
        
        if self.openai_client:
            models.extend([
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo-preview"
            ])
        
        if self.anthropic_client:
            models.extend([
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ])
        
        if self.perplexity_client:
            models.extend([
                "sonar",
                "sonar-small-chat",
                "sonar-small-online",
                "sonar-medium-chat",
                "sonar-medium-online",
                "llama-3.1-sonar-small-128k-chat",
                "llama-3.1-sonar-small-128k-online",
                "llama-3.1-sonar-large-128k-chat",
                "llama-3.1-sonar-large-128k-online",
                "llama-3.1-sonar-huge-128k-online"
            ])
        
        return models
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict]:
        """Get summary of a conversation"""
        conversation = self.conversation_manager.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return {
            "conversation_id": conversation_id,
            "message_count": len(conversation),
            "first_message": conversation[0].content[:100] + "..." if len(conversation[0].content) > 100 else conversation[0].content,
            "last_message": conversation[-1].content[:100] + "..." if len(conversation[-1].content) > 100 else conversation[-1].content,
            "created_at": conversation[0].timestamp,
            "updated_at": conversation[-1].timestamp
        }

# Global agent instance
agent = AIAgent()

import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

from langchain.chat_models import init_chat_model

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Default LLM provider
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    
    # Google Gemini settings
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")
    
    # Anthropic Claude settings
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model_name: str = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
    
    # Default parameter settings
    max_tokens_default: int = int(os.getenv("MAX_TOKENS_DEFAULT", "1000"))
    temperature_default: float = float(os.getenv("TEMPERATURE_DEFAULT", "0.3"))
    
    # System prompt settings
    default_prompt_type: str = os.getenv("DEFAULT_PROMPT_TYPE", "default")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance."""
    return Settings()


# Provider configuration mapping for consistent init_chat_model usage
# Format: (model_name, api_key, model_provider)
PROVIDER_CONFIG = {
    "openai": lambda s: (s.openai_model_name, s.openai_api_key, "openai"),
    "claude": lambda s: (s.anthropic_model_name, s.anthropic_api_key, "anthropic"),
    "gemini": lambda s: (s.gemini_model_name, s.gemini_api_key, "google_genai"),
}


class LLMHandler:
    """
    Handler for LLM interactions using LangChain with support for multiple providers.
    Uses init_chat_model consistently for all providers.
    """
    def __init__(self, provider: Optional[str] = None):
        self.settings = get_settings()
        self.provider = provider or self.settings.default_llm_provider
        logger.info(f"Using {self.provider} as LLM provider")
        self._initialize_model()
        # Session-based conversation history: {session_id: [(role, content), ...]}
        self.conversation_histories: dict[str, list[tuple[str, str]]] = {}
        self._default_session = "default"
    
    def _initialize_model(self):
        """Initialize the appropriate LLM model based on settings using init_chat_model."""
        if self.provider not in PROVIDER_CONFIG:
            logger.warning(f"Unknown provider '{self.provider}', defaulting to openai")
            self.provider = "openai"
        
        model_name, api_key, model_provider = PROVIDER_CONFIG[self.provider](self.settings)
        self.model = init_chat_model(model_name, model_provider=model_provider, api_key=api_key)
    
    def add_to_history(self, role: str, content: str, session_id: Optional[str] = None):
        """Add a message to conversation history for a specific session."""
        sid = session_id or self._default_session
        if sid not in self.conversation_histories:
            self.conversation_histories[sid] = []
        self.conversation_histories[sid].append((role, content))
    
    def clear_history(self, session_id: Optional[str] = None):
        """Clear conversation history for a specific session or all sessions."""
        if session_id:
            self.conversation_histories.pop(session_id, None)
        else:
            self.conversation_histories.clear()
    
    def get_history(self, session_id: Optional[str] = None) -> list[tuple[str, str]]:
        """Get conversation history for a specific session."""
        sid = session_id or self._default_session
        return self.conversation_histories.get(sid, []).copy()
    
    def invoke_with_history(
        self, 
        system_message: str, 
        user_message: str, 
        add_to_history: bool = False,
        session_id: Optional[str] = None
    ):
        """
        Invoke the model with conversation history.
        
        Args:
            system_message: System prompt for the LLM
            user_message: User message to add
            add_to_history: Whether to store this conversation in history
            session_id: Session identifier for history isolation
        
        Returns:
            Response from the LLM
        """
        sid = session_id or self._default_session
        
        # Build the full conversation
        messages = [("system", system_message)]
        messages.extend(self.get_history(sid))
        messages.append(("user", user_message))
        
        # Invoke the model
        response = self.model.invoke(messages)
        
        # Optionally add to history
        if add_to_history:
            self.add_to_history("user", user_message, sid)
            response_content = response.content if hasattr(response, "content") else str(response)
            self.add_to_history("assistant", response_content, sid)
        
        return response


# Create a singleton instance
llm_handler = LLMHandler() 
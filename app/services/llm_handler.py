import os
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI



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


class LLMHandler:
    """
    Handler for LLM interactions using LangChain with support for multiple providers.
    """
    def __init__(self, provider: Optional[str] = None):
        self.settings = get_settings()
        self.provider = provider or self.settings.default_llm_provider
        print(f"Using {self.provider} as LLM provider")
        self._initialize_model()
        # Initialize conversation history
        self.conversation_history = []
        # self._initialize_tokenizer()
    
    def _initialize_model(self):
        """Initialize the appropriate LLM model based on settings."""
        if self.provider == "openai":
            self.model = init_chat_model(
                self.settings.openai_model_name,
                api_key=self.settings.openai_api_key
            )
        elif self.provider == "claude":
            self.model = init_chat_model(
                self.settings.anthropic_model_name,
                api_key=self.settings.anthropic_api_key
            )
        elif self.provider == "gemini":
            # Use ChatGoogleGenerativeAI directly instead of init_chat_model
            self.model = ChatGoogleGenerativeAI(
                model=self.settings.gemini_model_name,
                google_api_key=self.settings.gemini_api_key
            )
        else:
            # Default to OpenAI if provider not recognized
            self.provider = "openai"  # Set to default
            self.model = init_chat_model(
                self.settings.openai_model_name,
                api_key=self.settings.openai_api_key
            )
    
    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append((role, content))
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_history(self):
        """Get current conversation history."""
        return self.conversation_history.copy()
    
    def invoke_with_history(self, system_message: str, user_message: str, add_to_history: bool = False):
        """
        Invoke the model with conversation history.
        
        Args:
            system_message: System prompt for the LLM
            user_message: User message to add
            add_to_history: Whether to store this conversation in history
        
        Returns:
            Response from the LLM
        """
        # Build the full conversation
        messages = [("system", system_message)]
        messages.extend(self.conversation_history)
        messages.append(("user", user_message))
        
        # Invoke the model
        response = self.model.invoke(messages)
        
        # Optionally add to history
        if add_to_history:
            self.add_to_history("user", user_message)
            response_content = response.content if hasattr(response, "content") else str(response)
            self.add_to_history("assistant", response_content)
        
        return response


# Create a singleton instance
llm_handler = LLMHandler() 
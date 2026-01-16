"""
LangChain agent configuration using modern APIs.
Uses create_tool_calling_agent instead of deprecated initialize_agent.
"""

import logging
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.services.llm_handler import LLMHandler
from app.services.prompt import get_system_prompt
from app.services.tools import ALL_TOOLS

load_dotenv()
logger = logging.getLogger(__name__)

# Store for session-based chat histories
_chat_histories: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create chat history for a session."""
    if session_id not in _chat_histories:
        _chat_histories[session_id] = InMemoryChatMessageHistory()
    return _chat_histories[session_id]


def clear_session_history(session_id: str) -> None:
    """Clear chat history for a specific session."""
    if session_id in _chat_histories:
        _chat_histories[session_id].clear()


def get_agent(session_id: str = "default") -> RunnableWithMessageHistory:
    """
    Initialize and return a modern LangChain agent with all resume editing tools.
    
    Uses create_tool_calling_agent which is the recommended approach for
    LLMs that support tool calling (OpenAI, Anthropic, Gemini, etc.)
    
    Args:
        session_id: Session identifier for conversation history isolation
    
    Returns:
        RunnableWithMessageHistory: Agent executor with message history support
    """
    llm = LLMHandler().model
    system_message = get_system_prompt("agent")
    
    # Create a prompt template with proper placeholders for the agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the tool-calling agent
    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )
    
    # Wrap with message history for session-based conversations
    agent_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    logger.info(f"Agent initialized for session: {session_id}")
    return agent_with_history


def run_agent(user_input: str, session_id: str = "default") -> str:
    """
    Run the agent with user input and return the response.
    
    Args:
        user_input: The user's message
        session_id: Session identifier for conversation history
    
    Returns:
        str: The agent's response
    """
    agent = get_agent(session_id)
    
    try:
        result = agent.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        
        # Handle different result types from the agent
        if isinstance(result, dict):
            output = result.get("output")
            # Return output if it's a non-empty string, otherwise provide a default
            if output:
                return output
            # If output is empty, the tool likely executed successfully
            return "Done! Your request has been processed."
        if hasattr(result, "output") and result.output:
            return result.output
        return str(result) if result else "Done! Your request has been processed."
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        return f"Error processing your request: {e}"

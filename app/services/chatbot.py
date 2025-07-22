import json
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from app.services.llm_handler import LLMHandler
from app.services.prompt import get_system_prompt
from app.services.resume import get_default_resume_content
from app.services.tools import ALL_TOOLS

load_dotenv()

def get_agent():
    """
    Initialize and return a LangChain agent with all resume editing tools.
    """
    llm = LLMHandler().model
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Use the dedicated agent prompt from prompt.py
    system_message = get_system_prompt("agent")
    
    agent = initialize_agent(
        ALL_TOOLS,
        llm,
        agent="chat-zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        memory=memory,
        agent_kwargs={
            "system_message": system_message
        }
    )
    return agent





    



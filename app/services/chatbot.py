import json
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from app.services.llm_handler import LLMHandler
from app.services.prompt import get_system_prompt
from app.services.resume_editor import get_resume_info
from app.services.tools import ALL_TOOLS

load_dotenv()

llm_chat = LLMHandler().model

def chat_with_bot(message: str):
    """
    Direct chat with the bot without tools - for conversations and analysis.
    """
    resume_content = get_resume_info()
    base_prompt = get_system_prompt()
    if resume_content:
        resume_json = json.dumps(resume_content.dict(), indent=2)
        system_prompt = (
            base_prompt
            + "\n\n---\nUSER RESUME INFORMATION :\n"
            + resume_json
            + "\n---\n"
            + "ALWAYS use the above USER RESUME INFORMATION when answering questions about the user's resume." 
            + "NEVER say you don't have the resume. If the user asks about their resume, refer to the above content."
        )
    else:
        system_prompt = (
            base_prompt
            + "\n\nNote: The user has not uploaded a resume yet. If asked about the resume, politely inform the user to upload one."
        )

    input_message = [("system", system_prompt), ("user", message)]
    print("Resume review LLM call invoked ")
    response = llm_chat.invoke(input_message)
    print("Resume review LLM call completed")
    
    # Extract content from response
    if hasattr(response, "content"):
        return response.content
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    return str(response)

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





    



from langchain_openai import ChatOpenAI
from langchain.agents import tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

from resume_editor import change_email, change_name, change_location

def parse_args(args: str) -> list[str]:
    return [a.strip() for a in args.split(",")]

@tool("Change Email")
def tool_change_email(args: str):
    "Change email in resume. Input should be: latex,new_email"
    latex, email = parse_args(args)
    return change_email(latex, email)

@tool("Change Name")
def tool_change_name(args: str):
    """
    Changes the name in the uploaded LaTeX resume.
    Input should be: latex,new_name
    Only use this tool if the user explicitly asks to update or change the name in their resume document.
    """
    latex, name = parse_args(args)
    return change_name(latex, name)

@tool("Change Location")
def tool_change_location(args: str):
    "Change location in resume. Input should be: latex,new_location"
    latex, location = parse_args(args)
    return change_location(latex, location)


@tool("Chat")
def tool_chat(message: str):
    """
    Respond conversationally to the user.
    Use this tool for all general questions, greetings, or when the user is not asking to edit the resume.
    """         
    return ChatOpenAI(model="gpt-3.5-turbo").invoke(message)


def get_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo")  # Or your preferred model
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        [tool_change_email, tool_change_name, tool_change_location, tool_chat],
        llm,
        agent="chat-zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )
    return agent

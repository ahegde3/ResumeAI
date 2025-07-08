from langchain_openai import ChatOpenAI
from langchain.agents import tool, initialize_agent
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
    "Change name in resume. Input should be: latex,new_name"
    latex, name = parse_args(args)
    return change_name(latex, name)

@tool("Change Location")
def tool_change_location(args: str):
    "Change location in resume. Input should be: latex,new_location"
    latex, location = parse_args(args)
    return change_location(latex, location)


def get_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo")  # Or your preferred model
    agent = initialize_agent(
        [tool_change_email, tool_change_name, tool_change_location],
        llm,
        agent="chat-zero-shot-react-description",
        verbose=True
    )
    return agent

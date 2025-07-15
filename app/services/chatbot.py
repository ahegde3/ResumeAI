from langchain_openai import ChatOpenAI
from langchain.agents import tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from app.services.llm_handler import LLMHandler
from app.services.prompt import get_system_prompt

from app.utils.file import get_latest_uploaded_file_content


from app.services.resume_editor import change_email, change_name, change_location, extract_resume_info, resume_to_latex ,latex_to_pdf
from app.utils.file import extract_file_content

load_dotenv()




llm_chat = LLMHandler().model

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


@tool("Chat", return_direct=True)
def tool_chat(message: str):
    """
    Respond conversationally to the user.
    Use this tool for all general questions, greetings, or when the user is not asking to edit the resume.
    """
    return "CHAT"
    # resume_content = get_latest_uploaded_file_content()
    # base_prompt = get_system_prompt()
    # if resume_content:
    #     system_prompt = (
    #         base_prompt
    #         + "\n\nThe user's uploaded resume content is below. Use this for any resume-related questions or edits:\n"
    #         + resume_content[:-1]  # Limit for context size
    #     )
    # else:
    #     system_prompt = (
    #         base_prompt
    #         + "\n\nNote: The user has not uploaded a resume yet. If asked about the resume, politely inform the user to upload one."
    #     )

    # response = llm_chat.invoke(message, system_prompt=system_prompt)
    # # If response is a Message object, extract the content
    # if hasattr(response, "content"):
    #     return response.content
    # # If response is a dict, extract the 'content' key
    # if isinstance(response, dict) and "content" in response:
    #     return response["content"]
    # # Otherwise, just return as string
    # return str(response)

@tool("Get Updated Resume", return_direct=True)
def tool_get_updated_resume(message: str):
    """
    Return the updated resume in LaTeX format using the latest Resume model data. Accepts a single string argument (user message) as required by ChatAgent.
    """
    # Get the latest LaTeX file content
    latex_content = extract_file_content("app/uploads/main.tex")
    # Extract the latest Resume model
    resume = extract_resume_info(latex_content)
    print(resume)
    # Render to LaTeX using the template
    latex = resume_to_latex(resume)
    latex_to_pdf(latex, "app/uploads/resume.pdf")
    return "DOne"


def chat_with_bot(message: str):
    resume_content = get_latest_uploaded_file_content()
    base_prompt = get_system_prompt()
    if resume_content:
        system_prompt = (
            base_prompt
            + "\n\n---\nUSER RESUME (for your reference):\n"
            + resume_content
            + "\n---\n"
            + "When the user asks about their resume, use the above content. Do NOT ask the user to paste their resume again."
        )
    else:
        system_prompt = (
            base_prompt
            + "\n\nNote: The user has not uploaded a resume yet. If asked about the resume, politely inform the user to upload one."
        )
    

    response = llm_chat.invoke(message, system_prompt=system_prompt)
    # If response is a Message object, extract the content
    if hasattr(response, "content"):
        return response.content
    # If response is a dict, extract the 'content' key
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    # Otherwise, just return as string
    return str(response)


def get_agent():
    # llm = ChatOpenAI(model="gpt-3.5-turbo")  # Or your preferred model
    llm = LLMHandler().model
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        [tool_change_email, tool_change_name, tool_change_location, tool_chat, tool_get_updated_resume],
        llm,
        agent="chat-zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )
    return agent





    



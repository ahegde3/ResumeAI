from langchain_openai import ChatOpenAI
from langchain.agents import tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from llm_handler import LLMHandler
from prompt import get_system_prompt
import os
load_dotenv()

from resume_editor import change_email, change_name, change_location

from pathlib import Path
import mimetypes
import PyPDF2
import docx
import csv
import json
import aiofiles


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
    
    print(system_prompt)
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
        [tool_change_email, tool_change_name, tool_change_location, tool_chat],
        llm,
        agent="chat-zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )
    return agent




def get_latest_uploaded_file_content(upload_dir="uploads"):
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    if not files:
        return None
    return extract_file_content(os.path.join(upload_dir, files[-1]))
    


def extract_file_content(file_path: str, max_length: int = 10000) -> str:
    """
    Extract content from a file based on its type.
    
    Args:
        file_path: Path to the file
        max_length: Maximum length of content to extract
        
    Returns:
        String containing the extracted content
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Text files
    if mime_type in ['text/plain', 'text/markdown', 'application/json', 'text/html', 'text/css', 'text/javascript'] or file_path.suffix in ['.txt', '.md', '.json', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.ts', '.tsx', '.jsx']:
        with aiofiles.open(file_path, 'r', errors='ignore') as f:
            content = f.read()
            return content[:max_length]
    
    # PDF files
    elif mime_type == 'application/pdf' or file_path.suffix == '.pdf':
        try:
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
                    
                    # Check if we've reached the max length
                    content = "\n\n".join(text)
                    if len(content) >= max_length:
                        return content[:max_length]
                        
            return "\n\n".join(text)
        except Exception as e:
            return f"Error extracting PDF content: {str(e)}"
    
    # Word documents
    elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] or file_path.suffix in ['.doc', '.docx']:
        try:
            doc = docx.Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            return content[:max_length]
        except Exception as e:
            return f"Error extracting Word document content: {str(e)}"
    
    # CSV files
    elif mime_type == 'text/csv' or file_path.suffix == '.csv':
        try:
            rows = []
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    rows.append(",".join(row))
                    if len("\n".join(rows)) >= max_length:
                        break
            return "\n".join(rows)[:max_length]
        except Exception as e:
            return f"Error extracting CSV content: {str(e)}"
    
    # Images and other binary files
    else:
        return f"[File content not extracted: {file_path.name} is a {mime_type or 'binary'} file]"

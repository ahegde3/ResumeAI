import json
from langchain_openai import ChatOpenAI
from langchain.agents import tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from app.services.llm_handler import LLMHandler
from app.services.prompt import get_system_prompt

from app.utils.file import get_latest_uploaded_file_content


from app.services.resume_editor import change_email, change_name, change_location, change_technical_skills, resume_to_latex ,latex_to_pdf,get_resume_info, change_experience_details
from app.utils.file import extract_file_content

load_dotenv()




llm_chat = LLMHandler().model

def parse_args(args: str) -> list[str]:
    return [a.strip() for a in args.split(",")]

@tool("Change Technical Skills", return_direct=True)
def tool_change_technical_skills(input_data: str):
    """
    Updates technical skills in the resume. 
    Input format: category_name|skill1,skill2,skill3
    Example: Programming Languages|Python,JavaScript,Java
    """
    print(f"Received input_data: {repr(input_data)}")
    print(f"Input type: {type(input_data)}")
    
    try:
        # Parse the pipe-separated format
        if "|" not in input_data:
            return f"Invalid format. Use: category|skill1,skill2,skill3. Got: {input_data}"
        
        parts = input_data.split("|", 1)
        if len(parts) != 2:
            return f"Invalid format. Use: category|skill1,skill2,skill3. Got: {input_data}"
        
        category = parts[0].strip()
        skills_str = parts[1].strip()
        
        # Parse skills
        items = [skill.strip() for skill in skills_str.split(",") if skill.strip()]
        
        if not category or not items:
            return f"Invalid input: Missing category or skills. Category: '{category}', Skills: {items}"
            
        print(f"Changing skills - Category: {category}, Items: {items}")
        
        change_technical_skills(category, items)
        return f"Technical skills updated successfully. Category: {category}, Items: {items}"
        
    except Exception as e:
        return f"Error updating technical skills: {e}. Input was: {repr(input_data)}"
    
@tool("Change Experience Details", return_direct=True)
def tool_change_experience_details(experience_input: str):
    """
    Update the experience details(work experience) in the resume.
    Use this tool when the user asks to update or change the work experience in their resume.
    Input format: company|bullet_point_1|bullet_point_2|bullet_point_3
    Example: Weekday|Enhanced platform functionality by delivering multiple end-to-end features|Reduced average time to hire candidates by 2 weeks|Boosted candidate engagement and response rates by 25%
    """
    print(f"Received experience_input: {repr(experience_input)}")
    print(f"Input type: {type(experience_input)}")
    
    try:
        if not experience_input or "|" not in experience_input:
            return "Invalid input format. Use: company|bullet_point_1|bullet_point_2|..."
        
        parts = experience_input.split("|")
        if len(parts) < 2:
            return "Invalid input format. Use: company|bullet_point_1|bullet_point_2|..."
        
        company = parts[0].strip()
        description_points = [point.strip() for point in parts[1:] if point.strip()]
        
        if not company:
            return "Company name is required"
        
        if not description_points:
            return "At least one description point is required"
        
        print(f"Company: {company}")
        print(f"Description points: {description_points}")
        
        change_experience_details(company, description_points)
        return f"Experience details updated for {company} with {len(description_points)} bullet points"
        
    except Exception as e:
        return f"Error updating experience details: {e}. Input was: {repr(experience_input)}"

@tool("Change Email", return_direct=True)
def tool_change_email(email: str):
    """Change email in resume. Input should be: new_email"""
    print("email", email)
    change_email(email)
    return "Email Id changed in resume"

@tool("Change Name", return_direct=True)
def tool_change_name(name: str):
    """
    Changes the name in the uploaded LaTeX resume.
    Input should be: new_name
    Only use this tool if the user explicitly asks to update or change the name in their resume document.
    """
    change_name(name)
    return "Name changed in resume"

@tool("Change Location", return_direct=True)
def tool_change_location(location: str):
    """Change location in resume. Input should be: new_location"""
    change_location(location)
    return "Location changed in resume"


@tool("Chat", return_direct=True)
def tool_chat(message: str):
    """
    Respond conversationally to the user.
    Use this tool for all general questions, greetings, or when the user is not asking to edit the resume.
    """
    return "CHAT"


@tool("Get Updated Resume", return_direct=True)
def tool_get_updated_resume(message: str):
    """
    Return the updated resume in LaTeX format using the latest Resume model data. Accepts a single string argument (user message) as required by ChatAgent.
    """
    # Get the latest LaTeX file content
    latex_content = extract_file_content("app/uploads/main.tex")
    # Extract the latest Resume model
    # resume = extract_resume_info(latex_content)
    # print(resume)
    # Render to LaTeX using the template
    latex = resume_to_latex()
    latex_to_pdf(latex, "app/uploads/resume.pdf")
    return "DOne"




def chat_with_bot(message: str):
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

    input_message= [("system", system_prompt), ("user", message)]
    response = llm_chat.invoke(input_message)
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
    
    # Custom system message for the agent
    system_message = """You are a helpful resume editing assistant. 

IMPORTANT TOOL USAGE INSTRUCTIONS:
- When using the "Change Technical Skills" tool, use the format: category|skill1,skill2,skill3
- Example: "Programming Languages|Python,JavaScript,Java"
- Do NOT use JSON format, use the pipe-separated format shown above

Always follow the exact format specified in each tool's description."""
    
    agent = initialize_agent(
        [tool_change_email,
          tool_change_name,
          tool_change_location,
          tool_chat,
          tool_get_updated_resume,
          tool_change_technical_skills,
          tool_change_experience_details
          ],
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





    



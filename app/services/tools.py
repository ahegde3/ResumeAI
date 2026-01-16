"""
LangChain tools for resume editing and analysis.
Uses Pydantic schemas for structured, validated tool inputs.
"""

import json
import logging
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.services.llm_handler import LLMHandler
from app.services.resume import (
    change_email, change_name, change_location, change_technical_skills, 
    resume_to_latex, latex_to_pdf, get_default_resume_content, change_experience_details,
    delete_technical_skill_category, delete_technical_skill_item, change_project_details,
    change_summary, remove_summary
)
from app.services.prompt import get_system_prompt

logger = logging.getLogger(__name__)
llm_handler = LLMHandler()


# =============================================================================
# Pydantic Input Schemas for Tools
# =============================================================================

class TechnicalSkillsInput(BaseModel):
    """Input schema for changing technical skills."""
    category: str = Field(description="Skill category name like 'Programming Languages', 'Frontend', 'Backend', etc.")
    items: list[str] = Field(description="List of skills to set for this category")


class BulkTechnicalSkillsInput(BaseModel):
    """Input schema for updating multiple skill categories at once."""
    categories: list[TechnicalSkillsInput] = Field(description="List of skill categories to update")


class ExperienceInput(BaseModel):
    """Input schema for changing experience details."""
    company: str = Field(description="Company name to update")
    description: list[str] = Field(description="List of bullet points describing the work experience")


class ProjectInput(BaseModel):
    """Input schema for changing project details."""
    name: str = Field(description="Project name to update")
    description: list[str] = Field(description="List of bullet points describing the project")
    tech: Optional[str] = Field(default=None, description="Optional technology stack used in the project")


class DeleteSkillInput(BaseModel):
    """Input schema for deleting technical skills."""
    operation: str = Field(description="Either 'CATEGORY' to delete entire category or 'ITEM' to delete specific skill")
    category: str = Field(description="Name of the skill category")
    item: Optional[str] = Field(default=None, description="Name of specific skill to delete (required if operation is 'ITEM')")


class SimpleTextInput(BaseModel):
    """Input schema for simple text inputs."""
    value: str = Field(description="The text value")


class JobDescriptionInput(BaseModel):
    """Input schema for job description analysis."""
    job_description: str = Field(description="The complete job description text to analyze")


class OptimizeResumeInput(BaseModel):
    """Input schema for auto-optimizing resume."""
    analysis_response: str = Field(
        default="AUTO",
        description="Pass 'AUTO' to use previous analysis from conversation history, or provide the analysis text directly"
    )


# =============================================================================
# Resume Editing Tools
# =============================================================================

@tool("change_technical_skills", args_schema=TechnicalSkillsInput)
def tool_change_technical_skills(category: str, items: list[str]) -> str:
    """
    Updates technical skills in the resume for a specific category.
    Use this when the user wants to update skills like Programming Languages, Frontend, Backend, etc.
    """
    logger.info(f"Changing technical skills - Category: {category}, Items: {items}")
    
    if not category:
        return "Error: Category name is required"
    if not items:
        return "Error: At least one skill item is required"
    
    try:
        change_technical_skills(category, items)
        return f"Technical skills updated successfully. Category: {category}, Items: {items}"
    except Exception as e:
        logger.error(f"Error updating technical skills: {e}")
        return f"Error updating technical skills: {e}"


@tool("update_all_technical_skills", args_schema=BulkTechnicalSkillsInput)
def tool_update_all_technical_skills(categories: list[TechnicalSkillsInput]) -> str:
    """
    Updates multiple technical skill categories at once in the resume.
    Use this when the user wants to update several skill categories simultaneously.
    """
    logger.info(f"Updating {len(categories)} skill categories")
    
    if not categories:
        return "Error: At least one category is required"
    
    updated = []
    errors = []
    
    for cat in categories:
        try:
            change_technical_skills(cat.category, cat.items)
            updated.append(f"{cat.category} ({len(cat.items)} skills)")
        except Exception as e:
            errors.append(f"{cat.category}: {e}")
    
    if errors:
        return f"Partially updated. Success: {updated}. Errors: {errors}"
    return f"All technical skills updated successfully: {updated}"


@tool("change_experience_details", args_schema=ExperienceInput)
def tool_change_experience_details(company: str, description: list[str]) -> str:
    """
    Update the work experience details in the resume for a specific company.
    Use this when the user asks to update or change their work experience bullet points.
    """
    logger.info(f"Changing experience for company: {company}")
    
    if not company:
        return "Error: Company name is required"
    if not description:
        return "Error: At least one description point is required"
    
    try:
        change_experience_details(company, description)
        return f"Experience details updated for {company} with {len(description)} bullet points"
    except Exception as e:
        logger.error(f"Error updating experience: {e}")
        return f"Error updating experience details: {e}"


@tool("change_project_details", args_schema=ProjectInput)
def tool_change_project_details(name: str, description: list[str], tech: Optional[str] = None) -> str:
    """
    Update project details in the resume.
    Use this when the user asks to update or change project experience in their resume.
    """
    logger.info(f"Changing project details for: {name}")
    
    if not name:
        return "Error: Project name is required"
    if not description:
        return "Error: At least one description point is required"
    
    try:
        change_project_details(name, description, tech)
        result = f"Project details updated for '{name}' with {len(description)} bullet points"
        if tech:
            result += f" and technology stack: {tech}"
        return result
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        return f"Error updating project details: {e}"


@tool("change_email", args_schema=SimpleTextInput)
def tool_change_email(value: str) -> str:
    """Change email address in the resume."""
    logger.info(f"Changing email to: {value}")
    change_email(value)
    return "Email changed in resume"


@tool("change_name", args_schema=SimpleTextInput)
def tool_change_name(value: str) -> str:
    """
    Changes the name in the resume.
    Only use this tool if the user explicitly asks to update or change the name.
    """
    logger.info(f"Changing name to: {value}")
    change_name(value)
    return "Name changed in resume"


@tool("change_location", args_schema=SimpleTextInput)
def tool_change_location(value: str) -> str:
    """Change location in the resume."""
    logger.info(f"Changing location to: {value}")
    change_location(value)
    return "Location changed in resume"


@tool("change_summary", args_schema=SimpleTextInput)
def tool_change_summary(value: str) -> str:
    """
    Update the summary section in the resume.
    Use this when the user asks to update, change, or add a summary to their resume.
    """
    logger.info("Updating resume summary")
    change_summary(value)
    return "Summary updated in resume"


@tool("remove_summary")
def tool_remove_summary() -> str:
    """
    Remove the summary section from the resume.
    Use this when the user asks to delete, remove, or clear the summary from their resume.
    """
    logger.info("Removing summary from resume")
    remove_summary()
    return "Summary section removed from resume"


@tool("delete_technical_skills", args_schema=DeleteSkillInput)
def tool_delete_technical_skills(operation: str, category: str, item: Optional[str] = None) -> str:
    """
    Delete technical skills from the resume.
    Use 'CATEGORY' operation to delete an entire skill category.
    Use 'ITEM' operation to delete a specific skill from a category.
    """
    logger.info(f"Deleting skills - Operation: {operation}, Category: {category}, Item: {item}")
    
    operation = operation.upper()
    
    if operation == "CATEGORY":
        success = delete_technical_skill_category(category)
        if success:
            return f"Successfully deleted entire '{category}' skill category from resume"
        return f"Category '{category}' not found in resume"
    
    elif operation == "ITEM":
        if not item:
            return "Error: Item name is required for ITEM operation"
        success = delete_technical_skill_item(category, item)
        if success:
            return f"Successfully deleted '{item}' from '{category}' category"
        return f"Either category '{category}' or skill '{item}' not found in resume"
    
    else:
        return f"Invalid operation '{operation}'. Use 'CATEGORY' or 'ITEM'"


# =============================================================================
# Conversation and Analysis Tools
# =============================================================================

@tool("chat", args_schema=SimpleTextInput)
def tool_chat(value: str) -> str:
    """
    Respond conversationally to the user.
    Use this tool for all general questions, greetings, or when the user is not asking to edit the resume.
    """
    system_prompt = get_system_prompt("default")
    input_message = [("system", system_prompt), ("user", value)]
    logger.info("Chat LLM call invoked")
    response = llm_handler.model.invoke(input_message)
    logger.info("Chat LLM call completed")
    
    # Extract content from response
    if hasattr(response, "content"):
        return response.content
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    return str(response)


@tool("clear_analysis_history")
def tool_clear_analysis_history() -> str:
    """
    Clears the conversation history from previous job description analyses.
    Use this when the user wants to start a fresh analysis or switch to analyzing a different job.
    """
    llm_handler.clear_history()
    return "Analysis history cleared. You can now start a fresh job description analysis."


@tool("get_updated_resume")
def tool_get_updated_resume() -> str:
    """
    Generate the updated resume as a PDF using the latest Resume model data.
    Use this when the user wants to see or download their updated resume.
    """
    latex = resume_to_latex()
    latex_to_pdf(latex, "app/uploads/resume.pdf")
    return "Resume updated and PDF generated successfully"


@tool("analyze_job_description", args_schema=JobDescriptionInput)
def tool_analyze_job_description(job_description: str) -> str:
    """
    Analyzes a job description and provides recommendations for resume improvements.
    Use this when the user provides a job description and wants to know how to improve their resume.
    """
    logger.info(f"Analyzing job description: {job_description[:100]}...")
    
    try:
        resume_content = get_default_resume_content()
        if not resume_content:
            return "No resume found. Please upload a resume first before analyzing job descriptions."
        
        analysis_prompt = f"""
        Analyze this job description and current resume to provide specific recommendations:
        
        JOB DESCRIPTION:
        {job_description}
        
        CURRENT RESUME:
        {json.dumps(resume_content.model_dump(), indent=2)}
        
        Please provide:
        1. Key skills mentioned in job description that are missing from resume
        2. Give a score from 0-100 of how well the resume matches the job description.
        3. Technical skills to add or emphasize.
        4. Experience descriptions that could be improved to match job requirements
        5. Specific action items for resume improvement
        
        Format your response as actionable recommendations.
        """
        
        response = llm_handler.invoke_with_history(
            system_message="You are a resume optimization expert.",
            user_message=analysis_prompt,
            add_to_history=True
        )
        
        if hasattr(response, "content"):
            return f"JOB DESCRIPTION ANALYSIS:\n\n{response.content}"
        return f"JOB DESCRIPTION ANALYSIS:\n\n{str(response)}"
        
    except Exception as e:
        logger.error(f"Error analyzing job description: {e}")
        return f"Error analyzing job description: {e}"


def _normalize_json_keys(data: dict) -> dict:
    """Recursively normalize all JSON keys to lowercase."""
    if isinstance(data, dict):
        return {k.lower(): _normalize_json_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_normalize_json_keys(item) for item in data]
    return data


@tool("auto_optimize_resume", args_schema=OptimizeResumeInput)
def tool_auto_optimize_resume(analysis_response: str = "AUTO") -> str:
    """
    Create an optimised resume by applying changes based on job description analysis.
    Pass 'AUTO' to use the previous analysis from conversation history.
    Or provide the analysis text directly.
    """
    logger.info("Auto-optimizing resume for job...")
    
    try:
        resume_content = get_default_resume_content()
        if not resume_content:
            return "No resume found. Please upload a resume first."
        
        use_history = analysis_response.strip().upper() == "AUTO"
        
        optimization_prompt_template = """
Based on {context}, suggest specific technical skills to add/update and experience improvements for this resume. Also, suggest a summary for the resume that matches the job description:

CURRENT RESUME:
{resume}

Please provide response in JSON format with lowercase keys:

{{
    "summary": "Summary of the resume that matches the job description",
    "technicalskills": [
        {{
            "category": "Programming Languages",
            "items": ["Python", "JavaScript/TypeScript", "Java", "Go", "C/C++"]
        }}
    ],
    "experience": [
        {{
            "company": "Company Name",
            "description": ["Bullet Point 1", "Bullet Point 2", "Bullet Point 3"]
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "tech": "Technology Stack",
            "description": ["Project Bullet Point 1", "Project Bullet Point 2"]
        }}
    ]
}}

Only suggest changes that would genuinely improve the match with the job requirements.
DO NOT HIGHLIGHT ANY SPECIFIC KEYWORD in **KEYWORD** format.
If no changes are needed for a section, omit that section.
"""
        
        if use_history:
            history = llm_handler.get_history()
            if not history:
                return "No previous analysis found in conversation history. Please run job description analysis first or provide the analysis response directly."
            
            optimization_prompt = optimization_prompt_template.format(
                context="our previous job description analysis conversation",
                resume=json.dumps(resume_content.model_dump(), indent=2)
            )
            
            response = llm_handler.invoke_with_history(
                system_message="You are a resume optimization expert. Provide only specific, actionable changes based on the previous job analysis conversation.",
                user_message=optimization_prompt,
                add_to_history=False
            )
        else:
            optimization_prompt = optimization_prompt_template.format(
                context=f"this job description analysis:\n{analysis_response}",
                resume=json.dumps(resume_content.model_dump(), indent=2)
            )
            
            response = llm_handler.model.invoke([
                ("system", "You are a resume optimization expert. Provide only specific, actionable changes."),
                ("user", optimization_prompt)
            ])
        
        content = response.content if hasattr(response, "content") else str(response)
        
        # Parse and apply changes from JSON response
        changes_made = []
        
        try:
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                raw_data = json.loads(json_content)
                # Normalize all keys to lowercase for consistent access
                parsed_data = _normalize_json_keys(raw_data)
                logger.info(f"Parsed data: {parsed_data}")
                
                # Handle Technical Skills (now checking lowercase key)
                if "technicalskills" in parsed_data:
                    for skill_category in parsed_data["technicalskills"]:
                        if "category" in skill_category and "items" in skill_category:
                            category = skill_category["category"]
                            items = skill_category["items"]
                            try:
                                change_technical_skills(category, items)
                                changes_made.append(f"Skills: {category}")
                            except Exception as e:
                                changes_made.append(f"Skills error ({category}): {e}")
                
                # Handle Experience Updates
                if "experience" in parsed_data:
                    for exp_item in parsed_data["experience"]:
                        if "company" in exp_item and "description" in exp_item:
                            company = exp_item["company"]
                            description_points = exp_item["description"]
                            try:
                                change_experience_details(company, description_points)
                                changes_made.append(f"Experience: {company}")
                            except Exception as e:
                                changes_made.append(f"Experience error ({company}): {e}")
                
                # Handle Project Updates
                if "projects" in parsed_data:
                    for project_item in parsed_data["projects"]:
                        if "name" in project_item and "description" in project_item:
                            project_name = project_item["name"]
                            description_points = project_item["description"]
                            tech_stack = project_item.get("tech", None)
                            try:
                                change_project_details(project_name, description_points, tech_stack)
                                changes_made.append(f"Project: {project_name}")
                            except Exception as e:
                                changes_made.append(f"Project error ({project_name}): {e}")

                # Handle Summary Updates
                if "summary" in parsed_data:
                    summary = parsed_data["summary"]
                    try:
                        change_summary(summary)
                        changes_made.append("Summary updated")
                    except Exception as e:
                        changes_made.append(f"Summary error: {e}")
                
                # Generate LaTeX and PDF
                latex = resume_to_latex()
                latex_to_pdf(latex, "app/uploads/resume.pdf")
                logger.info("Resume PDF generated")
                
                return f"RESUME AUTO-OPTIMIZATION COMPLETE:\n\nChanges applied: {changes_made}\n\nOPTIMIZATION SUGGESTIONS:\n{content}"
            
            else:
                return f"Could not extract valid JSON from response. Raw response:\n\n{content}"
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return f"Error parsing JSON response: {e}. Raw response:\n\n{content}"
        except Exception as e:
            logger.error(f"Error processing optimization: {e}")
            return f"Error processing optimization suggestions: {e}. Raw response:\n\n{content}"
            
    except Exception as e:
        logger.error(f"Error auto-optimizing resume: {e}")
        return f"Error auto-optimizing resume: {e}"


# =============================================================================
# Export all tools for easy import
# =============================================================================

ALL_TOOLS = [
    tool_change_email,
    tool_change_name,
    tool_change_location,
    tool_change_summary,
    tool_remove_summary,
    tool_chat,
    tool_clear_analysis_history,
    tool_get_updated_resume,
    tool_change_technical_skills,
    tool_update_all_technical_skills,
    tool_change_experience_details,
    tool_change_project_details,
    tool_analyze_job_description,
    tool_auto_optimize_resume,
    tool_delete_technical_skills
]

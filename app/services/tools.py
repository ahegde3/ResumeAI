"""
LangChain tools for resume editing and analysis.
"""

import json
from langchain.agents import tool
from app.services.llm_handler import LLMHandler
from app.services.resume_editor import (
    change_email, change_name, change_location, change_technical_skills, 
    resume_to_latex, latex_to_pdf, get_resume_info, change_experience_details
)

llm_handler = LLMHandler()

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

@tool("Update All Technical Skills", return_direct=True)
def tool_update_all_technical_skills(skills_data: str):
    """
    Updates multiple technical skill categories at once in the resume.
    Input format: category1|skill1,skill2;category2|skill3,skill4;category3|skill5,skill6
    Example: Programming Languages|Python,JavaScript;Frontend|React,NextJs;Backend|NodeJs,Express
    """
    print(f"Received skills_data: {repr(skills_data)}")
    
    try:
        if not skills_data or ";" not in skills_data:
            return "Invalid format. Use: category1|skill1,skill2;category2|skill3,skill4"
        
        updated_categories = []
        errors = []
        
        # Split by semicolon to get each category
        categories = skills_data.split(";")
        
        for category_data in categories:
            category_data = category_data.strip()
            if not category_data:
                continue
                
            if "|" not in category_data:
                errors.append(f"Missing pipe separator in: {category_data}")
                continue
            
            parts = category_data.split("|", 1)
            if len(parts) != 2:
                errors.append(f"Invalid format in: {category_data}")
                continue
            
            category = parts[0].strip()
            skills_str = parts[1].strip()
            
            # Parse skills
            items = [skill.strip() for skill in skills_str.split(",") if skill.strip()]
            
            if not category or not items:
                errors.append(f"Missing category or skills in: {category_data}")
                continue
            
            try:
                change_technical_skills(category, items)
                updated_categories.append(f"{category} ({len(items)} skills)")
            except Exception as e:
                errors.append(f"Error updating {category}: {e}")
        
        if errors:
            return f"Partially updated. Success: {updated_categories}. Errors: {errors}"
        else:
            return f"All technical skills updated successfully: {updated_categories}"
            
    except Exception as e:
        return f"Error updating technical skills: {e}. Input was: {repr(skills_data)}"
    
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

@tool("Clear Analysis History", return_direct=True)
def tool_clear_analysis_history(message: str):
    """
    Clears the conversation history from previous job description analyses.
    Use this when the user wants to start a fresh analysis or switch to analyzing a different job.
    """
    llm_handler.clear_history()
    return "Analysis history cleared. You can now start a fresh job description analysis."

@tool("Get Updated Resume", return_direct=True)
def tool_get_updated_resume(message: str):
    """
    Return the updated resume in LaTeX format using the latest Resume model data. 
    Accepts a single string argument (user message) as required by ChatAgent.
    """
    latex = resume_to_latex()
    latex_to_pdf(latex, "app/uploads/resume.pdf")
    return "Resume updated and PDF generated successfully"

@tool("Analyze Job Description", return_direct=True)
def tool_analyze_job_description(job_description: str):
    """
    Analyzes a job description and provides recommendations for resume improvements.
    Input should be the complete job description text.
    This tool will analyze the job requirements and suggest specific changes to make the resume more aligned.
    """
    print(f"Analyzing job description: {job_description[:100]}...")
    
    try:
        # Get current resume info
        resume_content = get_resume_info()
        if not resume_content:
            return "No resume found. Please upload a resume first before analyzing job descriptions."
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze this job description and current resume to provide specific recommendations:
        
        JOB DESCRIPTION:
        {job_description}
        
        CURRENT RESUME:
        {json.dumps(resume_content.dict(), indent=2)}
        
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
            add_to_history=True  # Store this analysis in conversation history
        )
        
        if hasattr(response, "content"):
            return f"JOB DESCRIPTION ANALYSIS:\n\n{response.content}"
        return f"JOB DESCRIPTION ANALYSIS:\n\n{str(response)}"
        
    except Exception as e:
        return f"Error analyzing job description: {e}"

@tool("Auto-Optimize Resume for Job", return_direct=True)
def tool_auto_optimize_resume(analysis_response: str):
    """
    Create an optimised resume by taking the response from the analysis tool and applying the changes to the resume.
    Use response from the tool_analyze_job_description tool to apply the changes to the resume.
    If analysis_response is "AUTO", it will use the conversation history from the previous analysis.
    """
    print(f"Auto-optimizing resume for job...")
    
    try:
        # Get current resume info
        resume_content = get_resume_info()
        if not resume_content:
            return "No resume found. Please upload a resume first."
        
        # Determine if we should use conversation history or provided analysis
        use_history = analysis_response.strip().upper() == "AUTO"
        
        if use_history:
            # Check if we have conversation history
            history = llm_handler.get_history()
            if not history:
                return "No previous analysis found in conversation history. Please run job description analysis first or provide the analysis response directly."
            
            # Create optimization prompt that references conversation history
            optimization_prompt = f"""
            Based on our previous job description analysis conversation, suggest specific technical skills to add/update and experience improvements for this resume:
            
            CURRENT RESUME:
            {json.dumps(resume_content.dict(), indent=2)}
            
            Please provide ONLY actionable changes in this format:

                         Please provide response in JSON format similar to the resume :

             Example:

             {{
                 "TechnicalSkills": [
                     {{
                         "category": "Programming Languages",
                         "items": ["Python", "JavaScript/TypeScript", "Java", "Go", "C/C++"]
                     }}
                 ],
                 "Experience": [
                     {{
                         "company": "Company Name",
                         "position": "Position",
                         "location": "Location",
                         "startDate": "Start Date",
                         "endDate": "End Date",
                         "description": ["Bullet Point 1", "Bullet Point 2", "Bullet Point 3"]
                     }}
                 ]
             }}
            

            
            Only suggest changes that would genuinely improve the match with the job requirements from our previous analysis.
            If no changes are needed for a section, omit that section.
            Use the insights from our previous analysis to make targeted recommendations.
            """
            
            response = llm_handler.invoke_with_history(
                system_message="You are a resume optimization expert. Provide only specific, actionable changes based on the previous job analysis conversation.",
                user_message=optimization_prompt,
                add_to_history=False  # Don't store optimization results in history
            )
            
            content = response.content if hasattr(response, "content") else str(response)
            
        else:
            # Use the provided analysis response to generate optimization suggestions
            optimization_prompt = f"""
            Based on this job description analysis, suggest specific technical skills to add/update and experience improvements:
            
            ANALYSIS RESPONSE:
            {analysis_response}
            
            CURRENT RESUME:
            {json.dumps(resume_content.dict(), indent=2)}
            
                         Please provide response in JSON format similar to the resume :

             Example:

             {{
                 "TechnicalSkills": [
                     {{
                         "category": "Programming Languages",
                         "items": ["Python", "JavaScript/TypeScript", "Java", "Go", "C/C++"]
                     }}
                 ],
                 "Experience": [
                     {{
                         "company": "Company Name",
                         "position": "Position",
                         "location": "Location",
                         "startDate": "Start Date",
                         "endDate": "End Date",
                         "description": ["Bullet Point 1", "Bullet Point 2", "Bullet Point 3"]
                     }}
                 ]
             }}
            
            Only suggest changes that would genuinely improve the match with the job requirements.
            If no changes are needed for a section, omit that section.
            """
            
            response = llm_handler.model.invoke([
                ("system", "You are a resume optimization expert. Provide only specific, actionable changes."),
                ("user", optimization_prompt)
            ])
            
            content = response.content if hasattr(response, "content") else str(response)
        
        # Parse and apply changes from JSON response
        changes_made = []
        
        try:
            # Try to extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                parsed_data = json.loads(json_content)
                
                # Handle Technical Skills
                if "TechnicalSkills" in parsed_data:
                    for skill_category in parsed_data["TechnicalSkills"]:
                        if "category" in skill_category and "items" in skill_category:
                            category = skill_category["category"]
                            items = skill_category["items"]
                            
                            # Convert to pipe format for existing function
                            skill_line = f"{category}|{','.join(items)}"
                            try:
                                
                                result = tool_change_technical_skills(skill_line)
                                changes_made.append(f"Skills: {result}")
                            except Exception as e:
                                changes_made.append(f"Skills error: {e}")
                
                # Handle Experience Updates
                if "Experience" in parsed_data:
                    for exp_item in parsed_data["Experience"]:
                        if "company" in exp_item and "description" in exp_item:
                            company = exp_item["company"]
                            description_points = exp_item["description"]
                            
                            # Convert to pipe format for existing function
                            exp_line = f"{company}|{'|'.join(description_points)}"
                            try:
                                result = tool_change_experience_details(exp_line)
                                changes_made.append(f"Experience: {result}")
                            except Exception as e:
                                changes_made.append(f"Experience error: {e}")
                
                if changes_made:
                    source = "conversation history" if use_history else "provided analysis"
                    return f"RESUME AUTO-OPTIMIZATION COMPLETE (using {source}):\n\n" + "\n".join(changes_made) + f"\n\nOPTIMIZATION SUGGESTIONS:\n{content}"
                else:
                    return f"ANALYSIS COMPLETE - No automatic changes suggested in JSON response:\n\n{content}"
            
            else:
                return f"Could not extract valid JSON from response. Raw response:\n\n{content}"
                
        except json.JSONDecodeError as e:
            return f"Error parsing JSON response: {e}. Raw response:\n\n{content}"
        except Exception as e:
            return f"Error processing optimization suggestions: {e}. Raw response:\n\n{content}"
            
    except Exception as e:
        return f"Error auto-optimizing resume: {e}"


# Export all tools for easy import
ALL_TOOLS = [
    tool_change_email,
    tool_change_name,
    tool_change_location,
    tool_chat,
    tool_clear_analysis_history,
    tool_get_updated_resume,
    tool_change_technical_skills,
    tool_update_all_technical_skills,
    tool_change_experience_details,
    tool_analyze_job_description,
    tool_auto_optimize_resume
] 
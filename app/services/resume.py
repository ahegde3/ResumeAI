import logging
import os
import tempfile
import subprocess
from typing import Optional

from app.models.resume import Resume, TechnicalSkillEntry, ExperienceEntry, ProjectEntry
from jinja2 import Environment, FileSystemLoader
from app.utils.util import escape_latex_special_chars, escape_data

logger = logging.getLogger(__name__)


class PDFGenerationError(Exception):
    """
    Custom exception for PDF generation failures.
    Provides structured error information including LaTeX logs.
    """
    def __init__(self, message: str, latex_log: Optional[str] = None, missing_packages: Optional[list[str]] = None):
        self.message = message
        self.latex_log = latex_log
        self.missing_packages = missing_packages or []
        super().__init__(self.message)
    
    def __str__(self):
        result = self.message
        if self.missing_packages:
            result += f"\nMissing packages: {', '.join(self.missing_packages)}"
        return result
    
    def to_dict(self) -> dict:
        """Convert error to dictionary for API responses."""
        return {
            "error": self.message,
            "latex_log": self.latex_log,
            "missing_packages": self.missing_packages,
        }

RESUME = {
  "name": "Anish Hegde",
  "location": "Boston, MA",
  "phone": "+1 (857)-313-4739",
  "email": "ahegde3@outlook.com",
  "linkedinUrl": "linkedin.com/in/ahegde3",
  "githubUrl": "github.com/ahegde3",
  "education": [
    {
      "degree": "Master of Science in Computer Science",
      "school": "Khoury College Of Computer Science - Northeastern University",
      "startDate": "Sep 2023",
      "endDate": "Dec 2025",
      "gpa": ""
    },
    {
      "degree": "Bachelor of Technology in Information Technology",
      "school": "Manipal Institute Of Technology",
      "startDate": "Aug 2016",
      "endDate": "Jul 2020",
      "gpa": ""
    }
  ],
  "experience": [
    {
      "company": "Wave Life Sciences",
      "position": "Software Developer(Co-op)",
      "location": "Cambridge, MA",
      "title": "Software Developer(Co-op)",
      "startDate": "Jul 2024",
      "endDate": "Dec 2024",
      "description": [
        "Built interactive React-based visualization tools for genomics data, accelerating drug discovery research timelines by 47% and improving cross-team collaboration between researchers and data scientists.",
        "Boosted application performance by 65% (targeting a reduction in load time from 10s to 3.5s) by implementing Redis caching and asynchronous programming patterns.",
      ]
    },
    {
      "company": "Weekday (YC W21)",
      "position": "FullStack Engineer",
      "location": "Remote, India",
      "title": "FullStack Engineer",
      "startDate": "Jun 2022",
      "endDate": "Aug 2023",
      "description": [
        "Built polished, user-centric frontend features in React, turning Figma designs into performant, accessible interfaces while improving Core Web Vitals by 30% by optimizing Redux state management and integrating with backend REST APIs.",
        "Strengthened application security and protected critical data by implementing GraphQL Shield rules, engineering custom authentication and authorization for sensitive mutations, for a lambda-based serverless microservice architecture.",
        "Cut backend latency by 18% for critical data endpoints by analyzing query execution plans to identify bottlenecks, rewriting inefficient SQL queries, and implementing strategic database indexes.",
      ]
    },
    {
      "company": "Merkle",
      "position": "Software Engineer",
      "location": "Mumbai, India",
      "title": "Software Engineer",
      "startDate": "Sep 2020",
      "endDate": "May 2022",
      "description": [
        "Designed and deployed a high-volume web crawling platform processing 300,000 URLs/day across 110+ retailers in multiple regions, enabling real-time competitive pricing and inventory tracking at scale. ",
        "Cut AWS EC2 and proxy costs by $7,000/month by re-architecting Kafka message consumption from a push-based to a pull-based model, improving crawler performance and reducing server crashes by 100%.",
        "Reduced analyst workflow time by 34% by building an internal React-based Chrome Extension that automated repetitive data extraction tasks, boosting productivity and accuracy across the team."
      ]
    },
        {
      "company": "Samsung Research",
      "position": "Software Engineer Intern",
      "location": "Bangalore, India",
      "title": "Software Engineer Intern",
      "startDate": "Jan 2020",
      "endDate": "Jun 2020",
      "description": [
        "Enabled real-time communication for IoT devices on SmartThings platform by developing MQTT protocol integration and message handling workflows supporting 5+ device categories.",
        "Reduced device onboarding time by 20% (from 5 min to 4 min average) by building automated workflows that optimized API endpoints and eliminated manual validation steps.",
        "Ensured reliable data persistence by implementing serverless functions that transformed MQTT payloads into structured formats, processing 10K+ messages daily with consistent schema validation.",
      ]
    }
  ],
  "projects": [
      {
          "name": "AI Teaching Assistant bot",
          "startDate": "Jan 2024",
          "endDate": "May 2024",
          "tech": "NextJs, FastAPI, Cloud Run,Pub/Sub, LLM",
          "description": [  
            "Designed a Pub/Sub-based ingestion pipeline for long-form video content, generating temporal embeddings in real time.",
            "Built a low-latency FastAPI microservice interfacing with LLMs for contextual QA, improving response times by 35%.",
            "Enhanced data accessibility and scalability through modular microservices integrated with distributed event queues."
          ]
      }
  ],
  "technicalSkills": [
    {
      "category": "Programming Languages",
      "items": ["Python", "JavaScript, TypeScript", "Java", "Go", "C/C++"]
    },
    {
      "category": "Frontend",
      "items": ["React", "NextJs", "Redux", "HTML5", "CSS", "Tailwind"]
    },
    {
      "category": "Backend",
      "items": ["Node.js", "Express", "FastAPI", "Kafka", "GraphQL", "REST", "gRPC"]
    },
    {
      "category": "Cloud",
      "items": [ "AWS (Lambda, EC2, RDS)","GCP", "Docker", "Kubernetes", "CI/CD", "Terraform", "NGINX"]
    },
    {
      "category": "Database & Caching",
      "items": ["PostgreSQL", "MySQL", "MongoDB","DynamoDB", "Redis", "Elasticsearch"]
    },
  ],
  "summary": "Software engineer experienced in designing and delivering scalable, high-performance systems across backend, frontend, and cloud environments. Proven track record of building products end-to-end — from architecting distributed systems and optimizing backend services to developing intuitive user interfaces."
}



def get_default_resume_content():
    escaped_resume_data = escape_data(RESUME)
    resume = Resume.model_validate(escaped_resume_data)
    return resume


resume_info = get_default_resume_content()


def reset_resume():
    """
    Reset the resume_info to the original default state.
    Use this when starting analysis for a new job description.
    """
    global resume_info
    resume_info = get_default_resume_content()
    print("Resume reset to original state")


def change_technical_skills(category: str, items: list[str]):
    # Escape LaTeX special characters in each item and category
    escaped_items = [escape_latex_special_chars(item) for item in items]
    escaped_category = escape_latex_special_chars(category)
    escaped_category_lower = escaped_category.lower()

    for skill in resume_info.technicalSkills:
        # Compare escaped versions for accurate matching
        skill_category_lower = skill.category.lower()
        if (skill_category_lower == escaped_category_lower or 
            skill_category_lower in escaped_category_lower or 
            escaped_category_lower in skill_category_lower):
            skill.category = escaped_category
            skill.items = escaped_items
            print(f"Changed technical skills for {category}")
            return
    
    # No match found, add new entry
    resume_info.technicalSkills.append(TechnicalSkillEntry(
        category=escaped_category,
        items=escaped_items
    ))
    print(f"Added new technical skills for {category}")
        
def change_experience_details(company: str, description: list[str]):

    escaped_description = [escape_latex_special_chars(item) for item in description]
    escaped_company = escape_latex_special_chars(company)
    escaped_company_lower = escaped_company.lower()
    
    for experience in resume_info.experience:
        # Compare escaped versions for accurate matching
        experience_company_lower = experience.company.lower()
        # Check for exact match or partial match in either direction
        if (escaped_company_lower == experience_company_lower or 
            escaped_company_lower in experience_company_lower or 
            experience_company_lower in escaped_company_lower):
            experience.description = escaped_description
            print(f"Changed experience details for {company}")
            return
    resume_info.experience.append(ExperienceEntry(
        company=escaped_company,
        description=escaped_description
    ))
    print(f"Added new experience details for {company}")


def change_project_details(project_name: str, description: list[str], tech: str = None):
    """
    Update project details in the resume.
    
    Args:
        project_name: Name of the project to update/add
        description: List of description bullet points
        tech: Optional technology stack string
    """
    escaped_description = [escape_latex_special_chars(item) for item in description]
    escaped_project_name = escape_latex_special_chars(project_name)
    escaped_project_name_lower = escaped_project_name.lower()
    escaped_tech = escape_latex_special_chars(tech) if tech else None
    
    for project in resume_info.projects:
        # Compare escaped versions for accurate matching
        project_name_lower = project.name.lower()
        # Check for exact match or partial match in either direction
        if (escaped_project_name_lower == project_name_lower or 
            escaped_project_name_lower in project_name_lower or 
            project_name_lower in escaped_project_name_lower):
            project.description = escaped_description
            if escaped_tech:
                project.tech = escaped_tech
            print(f"Changed project details for {project_name}")
            return
    
    # No match found, add new project entry
    new_project = ProjectEntry(
        name=escaped_project_name,
        description=escaped_description
    )
    if escaped_tech:
        new_project.tech = escaped_tech
    
    resume_info.projects.append(new_project)
    print(f"Added new project details for {project_name}")


def change_email( new_email):
    resume_info.email = new_email


def change_name(new_name):
    resume_info.name = new_name

def change_location(new_location):
    resume_info.location = new_location

def change_summary(new_summary: str):
    """
    Update the summary section in the resume.
    
    Args:
        new_summary: The new summary text to set
    """
    escaped_summary = escape_latex_special_chars(new_summary)
    resume_info.summary = escaped_summary
    print(f"Changed summary to: {new_summary[:50]}...")

def remove_summary():
    """
    Remove the summary section from the resume by setting it to empty string.
    """
    resume_info.summary = ""
    print("Summary section removed from resume")


def delete_technical_skill_category(category: str):
    """
    Delete an entire technical skill category from the resume.
    """
    escaped_category = escape_latex_special_chars(category)
    escaped_category_lower = escaped_category.lower()
    
    # Find and remove the category
    for i, skill in enumerate(resume_info.technicalSkills):
        skill_category_lower = skill.category.lower()
        if (skill_category_lower == escaped_category_lower or 
            skill_category_lower in escaped_category_lower or 
            escaped_category_lower in skill_category_lower):
            removed_category = resume_info.technicalSkills.pop(i)
            print(f"Deleted technical skill category: {removed_category.category}")
            return True
    
    print(f"Category '{category}' not found")
    return False


def delete_technical_skill_item(category: str, item: str):
    """
    Delete a specific technical skill item from a category.
    """
    escaped_category = escape_latex_special_chars(category)
    escaped_item = escape_latex_special_chars(item)
    escaped_category_lower = escaped_category.lower()
    escaped_item_lower = escaped_item.lower()
    
    # Find the category
    for skill in resume_info.technicalSkills:
        skill_category_lower = skill.category.lower()
        if (skill_category_lower == escaped_category_lower or 
            skill_category_lower in escaped_category_lower or 
            escaped_category_lower in skill_category_lower):
            
            # Find and remove the item
            for i, skill_item in enumerate(skill.items):
                skill_item_lower = skill_item.lower()
                if (skill_item_lower == escaped_item_lower or 
                    skill_item_lower in escaped_item_lower or 
                    escaped_item_lower in skill_item_lower):
                    removed_item = skill.items.pop(i)
                    print(f"Deleted '{removed_item}' from '{skill.category}' category")
                    
                    # If category becomes empty, remove it entirely
                    if not skill.items:
                        resume_info.technicalSkills.remove(skill)
                        print(f"Category '{skill.category}' was empty and has been removed")
                    
                    return True
            
            print(f"Item '{item}' not found in category '{skill.category}'")
            return False
    
    print(f"Category '{category}' not found")
    return False


def resume_to_latex() -> str:
    """
    Render the Resume model as a LaTeX string using the uploads/main.tex template.
    """
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../uploads')),
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        autoescape=False
    )

    template = env.get_template('main.tex')
    return template.render(resume=resume_info)


def write_latex_resume(latex: str, output_path: str = 'app/uploads/main2.tex'):
    """
    Write the LaTeX string to uploads/main.tex (overwrite).
    """
    with open(output_path, 'w') as f:
        f.write(latex)



def _read_latex_log(temp_dir: str) -> Optional[str]:
    """Read the LaTeX log file if it exists."""
    log_path = os.path.join(temp_dir, 'document.log')
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    return None


def _extract_missing_packages(log_content: str) -> list[str]:
    """Extract missing package names from LaTeX log."""
    missing = []
    if not log_content:
        return missing
    
    # Common patterns for missing packages
    import re
    patterns = [
        r"! LaTeX Error: File `(.+?)\.sty' not found",
        r"! Package (.+?) Error",
        r"Package (.+?) not found",
        r"! I can't find file `(.+?)'",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, log_content)
        missing.extend(matches)
    
    return list(set(missing))


def latex_to_pdf(latex_str: str, output_path: str = 'output.pdf') -> str:
    """
    Convert LaTeX string to PDF.
    
    Args:
        latex_str: The LaTeX content to compile
        output_path: Path where the PDF should be saved
    
    Returns:
        str: Path to the generated PDF
    
    Raises:
        PDFGenerationError: If PDF generation fails with detailed error info
    """
    # Check if pdflatex is available
    try:
        subprocess.run(['which', 'pdflatex'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise PDFGenerationError(
            "pdflatex is not installed or not found in PATH. "
            "Please install LaTeX distribution (e.g., BasicTeX on macOS: brew install --cask basictex) "
            "and ensure /Library/TeX/texbin is in your PATH."
        )
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = os.path.join(temp_dir, 'document.tex')

        # Write LaTeX string to a .tex file
        with open(tex_path, 'w') as tex_file:
            tex_file.write(latex_str)

        # Run pdflatex to generate the PDF
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            stdout_output = e.stdout.decode() if e.stdout else ""
            stderr_output = e.stderr.decode() if e.stderr else ""
            latex_log = _read_latex_log(temp_dir)
            missing_packages = _extract_missing_packages(latex_log or stdout_output)
            
            error_msg = "LaTeX compilation failed."
            if missing_packages:
                error_msg += f" Missing packages detected: {', '.join(missing_packages)}. "
                error_msg += "Install them using 'sudo tlmgr install <package-name>'."
            
            logger.error(f"LaTeX compilation failed:\nstdout: {stdout_output}\nstderr: {stderr_output}")
            
            raise PDFGenerationError(
                message=error_msg,
                latex_log=latex_log,
                missing_packages=missing_packages
            )
        except FileNotFoundError:
            raise PDFGenerationError(
                "pdflatex command not found. Please install LaTeX distribution and ensure it's in your PATH."
            )

        # Check if PDF was generated
        generated_pdf = os.path.join(temp_dir, 'document.pdf')
        if not os.path.exists(generated_pdf):
            latex_log = _read_latex_log(temp_dir)
            raise PDFGenerationError(
                message="PDF generation failed - no output file was created.",
                latex_log=latex_log
            )
        
        # Move the resulting PDF to the desired location
        os.replace(generated_pdf, output_path)
        logger.info(f"PDF generated at: {output_path}")
        return output_path





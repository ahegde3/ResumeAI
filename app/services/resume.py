
from app.models.resume import Resume, TechnicalSkillEntry, ExperienceEntry, ProjectEntry
from jinja2 import Environment, FileSystemLoader
import os
import tempfile
import subprocess
from app.utils.util import escape_latex_special_chars, escape_data

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
      "company": "Toddle",
      "position": "Software Engineer Backend",
      "location": "Remote, India",
      "title": "Software Engineer Backend",
      "startDate": "Mar 2023",
      "endDate": "Aug 2023",
      "description": [
        "Expanded backend API capabilities by developing and deploying over 15 new GraphQL resolvers and mutations within an AWS Lambda-based serverless microservice architecture.",
        "Strengthened application security and protected critical data by implementing GraphQL Shield rules, engineering custom authorization for sensitive mutations, and resolving vulnerabilities, ensuring compliance with regulations.",
        "Cut backend latency by 18% for critical data endpoints by analyzing query execution plans to identify bottlenecks, rewriting inefficient SQL queries, and implementing strategic database indexes."
      ]
    },
    {
      "company": "Weekday (YC W21)",
      "position": "FullStack Engineer (Contract)",
      "location": "Remote, India",
      "title": "FullStack Engineer",
      "startDate": "Jun 2022",
      "endDate": "Feb 2023",
      "description": [
        "Built polished, user-centric frontend features in React, turning Figma designs into performant, accessible interfaces while integrating with backend REST APIs (Node.js, Express).",
        "Improved engagement by 25% by creating a unified messaging dashboard that consolidated recruiter conversations across multiple platforms into a single contextual view."
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
    }
  ],
  "projects": [
      {
          "name": "AI Teaching Assistant bot",
          "startDate": "Jan 2024",
          "endDate": "May 2024",
          "tech": "NextJs, FastAPI, Cloud Run,Pub/Sub, LLM",
          "description": [
            "Built a scalable MLOps pipeline for processing long-form video lectures, generating temporal-based vector embeddings, and orchestrating workflows using an event-driven Pub/Sub architecture on GCP.  ",
            "Reduced analyst workflow time by 34% by building an internal React-based Chrome Extension that automated repetitive data extraction tasks, boosting productivity and accuracy across the team"
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
      "items": ["NodeJs", "Express", "FastAPI", "Apache Kafka", "GraphQL", "REST", "gRPC"]
    },
    {
      "category": "Cloud",
      "items": ["GCP", "AWS", "Docker", "Kubernetes", "CI/CD"]
    },
    {
      "category": "Database",
      "items": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch"]
    },
  ],
  "summary": "Software engineer experienced in designing and delivering scalable, high-performance systems across backend, frontend, and cloud environments. Proven track record of building products end-to-end — from architecting distributed systems and optimizing backend services to developing intuitive user interfaces."
}



def get_default_resume_content():
    escaped_resume_data = escape_data(RESUME)
    resume = Resume.model_validate(escaped_resume_data)
    return resume


resume_info = get_default_resume_content()


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
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
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



def latex_to_pdf(latex_str, output_path='output.pdf'):
    # Check if pdflatex is available
    try:
        subprocess.run(['which', 'pdflatex'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise RuntimeError(
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
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            error_msg = "LaTeX compilation failed. This might be due to missing LaTeX packages."
            stdout_output = e.stdout.decode() if e.stdout else ""
            stderr_output = e.stderr.decode() if e.stderr else ""
            
            # Check for common missing package errors
            if "not found" in stdout_output or "not found" in stderr_output:
                error_msg += " Please install missing LaTeX packages using 'sudo tlmgr install <package-name>'."
            
            print("LaTeX compilation failed:")
            print(stdout_output)
            print(stderr_output)
            raise RuntimeError(error_msg)
        except FileNotFoundError:
            raise RuntimeError(
                "pdflatex command not found. Please install LaTeX distribution and ensure it's in your PATH."
            )

        # Check if PDF was generated
        generated_pdf = os.path.join(temp_dir, 'document.pdf')
        if not os.path.exists(generated_pdf):
            raise RuntimeError("PDF generation failed - no output file was created.")
        
        # Move the resulting PDF to the desired location
        os.replace(generated_pdf, output_path)
        print(f"PDF generated at: {output_path}")





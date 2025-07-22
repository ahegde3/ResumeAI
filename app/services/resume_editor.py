import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.services.llm_handler import LLMHandler
from app.models.resume import Resume, TechnicalSkillEntry, ExperienceEntry
from jinja2 import Environment, FileSystemLoader
import os
import tempfile
import subprocess
import shutil
import os
import subprocess
import tempfile
from app.utils.file import extract_file_content


def escape_latex_special_chars(text: str) -> str:
    """
    Escape special characters in text for LaTeX formatting.
    Replaces special characters with their escaped versions using backslashes.
    """
    # Dictionary of LaTeX special characters and their escaped versions
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '^': r'\^{}',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    
    # Replace each special character with its escaped version
    for char, escaped in latex_special_chars.items():
        text = text.replace(char, escaped)
    
    return text


def unescape_latex_special_chars(text: str) -> str:
    """
    Unescape LaTeX special characters back to normal text.
    """
    # Dictionary of escaped LaTeX characters and their unescaped versions
    latex_escaped_chars = {
        r'\&': '&',
        r'\%': '%',
        r'\$': '$',
        r'\#': '#',
        r'\^{}': '^',
        r'\_': '_',
        r'\{': '{',
        r'\}': '}',
    }
    
    # Replace each escaped character with its unescaped version
    for escaped, char in latex_escaped_chars.items():
        text = text.replace(escaped, char)
    
    return text


def escape_resume_data(data):
    """
    Recursively escape LaTeX special characters in all string fields of the resume data.
    Handles nested dictionaries, lists, and string values.
    """
    if isinstance(data, dict):
        return {key: escape_resume_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [escape_resume_data(item) for item in data]
    elif isinstance(data, str):
        return escape_latex_special_chars(data)
    else:
        # Return other types (int, float, bool, None) unchanged
        return data

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


def change_email( new_email):
    resume_info.email = new_email


def change_name(new_name):
    resume_info.name = new_name

def change_location(new_location):
    resume_info.location = new_location



RESUME = {
  "name": "Anish Hegde",
  "location": "Boston, MA",
  "phone": "+1 (857)-313-4739",
  "email": "hegde.anis@northeastern.edu",
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
      "location": "Cambridge,MA",
      "title": "Software Developer(Co-op)",
      "startDate": "Jul 2024",
      "endDate": "Dec 2024",
      "description": [
        "Enhanced researcher efficiency by 47% by developing UI in React for complex data visualization and interaction.",
        "Boosted application performance by 65% (targeting a reduction in load time from 10s to 3.5s) by implementing Redis caching and asynchronous programming patterns.",
        "Devised and implemented a robust data persistence strategy, integrating local storage with backend caching to ensure a fluid and uninterrupted user experience across multiple sessions."
      ]
    },
    {
      "company": "Toddle",
      "position": "Software Engineer Backend",
      "location": "Remote,India",
      "title": "Software Engineer Backend",
      "startDate": "Apr 2023",
      "endDate": "Aug 2023",
      "description": [
        "Expanded backend API capabilities by developing and deploying over 15 new GraphQL resolvers and mutations within an AWS Lambda-based serverless microservice architecture.",
        "Strengthened application security and protected critical data by implementing GraphQL Shield rules, engineering custom authorization for sensitive mutations, and resolving Dataloader caching vulnerabilities.",
        "Cut backend latency by 18% for critical data endpoints by analyzing query execution plans to identify bottlenecks, rewriting inefficient SQL queries, and implementing strategic database indexes."
      ]
    },
    {
      "company": "Weekday (YC W21)",
      "position": "FullStack Engineer",
      "location": "Remote,India",
      "title": "FullStack Engineer",
      "startDate": "Jun 2022",
      "endDate": "Feb 2023",
      "description": [
        "Enhanced platform functionality by delivering multiple end-to-end features, which involved scoping requirements, developing REST APIs (Node.js, Express), and translating Figma mockups into functional React UI components.",
        "Reduced average time to hire candidates by 2 weeks (28%) by leading the development of a new candidate inbound sourcing strategy.",
        "Boosted candidate engagement and response rates by 25% by engineering a unified messaging system that consolidated communication over different channels into a single contextual view for recruiters."
      ]
    },
    {
      "company": "Merkle",
      "position": "Software Engineer",
      "location": "Mumbai,India",
      "title": "Software Engineer",
      "startDate": "Sep 2020",
      "endDate": "May 2022",
      "description": [
        "Achieved $7,000 in monthly AWS EC2 and proxy cost savings by designing and implementing a high-volume NodeJS-based web crawling product (processing 300,000 URLs daily from 110+ retailers) and re-architecting Kafka message consumption from a push to a pull-based model for improved performance.",
        "Resolved critical performance bottlenecks and stability issues, cutting CPU usage by 37% and eliminating 100% of message-related server crashes, by executing an architectural shift in Kafka consumption model.",
        "Reduced analyst workflow effort by 34% by conceptualizing and building an internal React-based Chrome Extension, streamlining data access and manipulation tasks."
      ]
    }
  ],
  "projects": [
      {
          "name": "AI Teaching Assistant bot",
          "startDate": "Jan 2024",
          "endDate": "Present",
          "tech": "NextJs, FastAPI, Cloud Run,Pub/Sub, LLM",
          "description": [
            "Engineered a scalable MLOps pipeline capable of processing videos of unlimited length, overcoming the previous 10-minute hard limit, by migrating the core workflow to an asynchronous, Pub/Sub-triggered architecture on GCP.",
            "Improved student comprehension and retention rates by 30% , engineering an innovative interactive chatbot service designed to enhance learner engagement with video lecture content."
          ]
      }
  ],
  "technicalSkills": [
    {
      "category": "Programming Languages",
      "items": ["Python", "JavaScript/TypeScript", "Java", "Go", "C/C++"]
    },
    {
      "category": "Frontend",
      "items": ["React", "NextJs", "Redux", "HTML5", "CSS", "Tailwind"]
    },
    {
      "category": "Backend",
      "items": ["NodeJs", "Express", "FastAPI", "Flask", "Apache Kafka", "GraphQL", "REST", "gRPC"]
    },
    {
      "category": "Cloud & DevOps",
      "items": ["GCP", "AWS", "Docker", "Kubernetes", "CI/CD", "Git"]
    },
    {
      "category": "Database",
      "items": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Neo4j"]
    },
  ]
}

# Add more as needed

EXTRACTION_PROMPT = """
You are an information extraction assistant. Given a LaTeX resume, extract the following fields as accurately as possible:
- Name
- Location
- Phone Number

Return your answer in this JSON format:

{{
  "name": "",
  "location": "",
  "phone": "",
  "email": "",
  "linkedinUrl": "",
  "githubUrl": "",

  "education": [
    {{
      "degree": "",
      "school": "",
      "startDate": "",
      "endDate": "",
      "gpa": ""
    }}
  ],
  "experience": [
    {{
      "company": "",
      "position": "",
      "location": "",
      "title": "",
      "startDate": "",
      "endDate": "",
      "description": ""
    }}
    ]
}}

Here is the LaTeX resume:
----------------------
{resume}
----------------------
"""


llm_extractor = LLMHandler().model

# Prepare prompt template
template = EXTRACTION_PROMPT
prompt = PromptTemplate.from_template(template)
# Build the chain
chain = LLMChain(llm=llm_extractor, prompt=prompt)


def extract_resume_info(resume: str = None):
    # response = chain.run(resume=resume)
    # # Remove Markdown code block markers if present
    # if response.strip().startswith('```'):
    #     response = response.strip().lstrip('`').split('\n', 1)[-1]
    #     if response.strip().startswith('json'):
    #         response = response.strip()[4:]
    #     response = response.strip()
    #     if response.endswith('```'):
    #         response = response[:response.rfind('```')].strip()
    # print(response)
    # resume = Resume.model_validate_json(response)
    
    # Escape LaTeX special characters in all string fields before model creation
    escaped_resume_data = escape_resume_data(RESUME)
    resume = Resume.model_validate(escaped_resume_data)
    return resume


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
    print(resume_info)
    template = env.get_template('main.tex')
    return template.render(resume=resume_info)


def write_latex_resume(latex: str, output_path: str = 'app/uploads/main2.tex'):
    """
    Write the LaTeX string to uploads/main.tex (overwrite).
    """
    with open(output_path, 'w') as f:
        f.write(latex)


# def latex_to_pdf(latex: str, output_pdf_path: str) -> bool:
#     """
#     Compile a LaTeX string to a PDF file using the 'latex' Python library.
#     Args:
#         latex: The LaTeX source as a string.
#         output_pdf_path: The path where the resulting PDF should be saved.
#     Returns:
#         True if PDF was generated successfully, False otherwise.
#     """
#     if shutil.which("pdflatex") is None:
#         print("Error: 'pdflatex' is not installed or not found in PATH. Please install a LaTeX distribution (e.g., MacTeX, TeX Live) and ensure 'pdflatex' is available.")
#         return False
#     try:
#         pdf = build_pdf(latex)
#         pdf.save_to(output_pdf_path)
#         return True
#     except LatexBuildError as e:
#         print(f"LaTeX build error: {e}")
#         return False
#     except Exception as e:
#         print(f"Error during LaTeX to PDF conversion: {e}")
#         return False





def latex_to_pdf(latex_str, output_path='output.pdf'):
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
            print("LaTeX compilation failed:")
            print(e.stdout.decode())
            print(e.stderr.decode())
            raise RuntimeError("LaTeX compilation failed.")

        # Move the resulting PDF to the desired location
        generated_pdf = os.path.join(temp_dir, 'document.pdf')
        os.replace(generated_pdf, output_path)
        print(f"PDF generated at: {output_path}")


resume_info = extract_resume_info(None)


def get_resume_info():
    return resume_info
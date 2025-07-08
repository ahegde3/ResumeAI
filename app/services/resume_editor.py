import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.services.llm_handler import LLMHandler

def change_email(latex, new_email):
    return re.sub(r'\\email\{[^\}]*\}', f'\\email{{{new_email}}}', latex)

def change_name(latex, new_name):
    return re.sub(r'\\name\{[^\}]*\}', f'\\name{{{new_name}}}', latex)

def change_location(latex, new_location):
    return re.sub(r'\\location\{[^\}]*\}', f'\\location{{{new_location}}}', latex)

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
  "phone": ""
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


def extract_resume_info(resume: str):
    response = chain.run(resume=resume)
    print(response)
    return response




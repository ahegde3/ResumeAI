from pydantic import BaseModel, Field
from typing import List

class EducationEntry(BaseModel):
    degree: str = ""
    school: str = ""
    startDate: str = ""
    endDate: str = ""
    gpa: str = ""

class ExperienceEntry(BaseModel):
    company: str = ""
    position: str = ""
    location: str = ""
    title: str = ""
    startDate: str = ""
    endDate: str = ""
    description: str = ""

class Resume(BaseModel):
    name: str = ""
    location: str = ""
    phone: str = ""
    email: str = ""
    linkedinUrl: str = ""
    githubUrl: str = ""
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)

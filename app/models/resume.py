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
    description: List[str] = Field(default_factory=list)

class ProjectEntry(BaseModel):
    name: str = ""
    startDate: str = ""
    endDate: str = ""
    tech: str = ""
    description: List[str] = Field(default_factory=list)    

class TechnicalSkillEntry(BaseModel):
    category: str = ""
    items: List[str] = Field(default_factory=list)

class Resume(BaseModel):
    name: str = ""
    location: str = ""
    phone: str = ""
    email: str = ""
    linkedinUrl: str = ""
    githubUrl: str = ""
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    technicalSkills: List[TechnicalSkillEntry] = Field(default_factory=list)

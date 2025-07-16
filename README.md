# Resume AI

## Description

Ever faced an issue where you have to change the resume detail for each job description?

The bot will help you with that

- Review your resume with the job description.
- Suggest issues and score your resume out of 100.
- Using chatbot you can change the resume details.
- Print the resume in pdf format.

## Tech Stack

- Python
- FastAPI
- Langchain
- LaTeX
- HTML
- CSS

## Setup

```bash
poetry install
```

To run the bot

```bash
 poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Go to http://localhost:8000 to play with the bot.

## Road map

- [x] Ability to review the resume with the job description.
- [x] ABility to generate pdf from latex resume.
- [x] Ability to change name,email,location,technical skills,experience details.
- [ ] Better readable response
- [ ] Inmprove the inellegience of resume generation
- [ ] Single step review and updated resume generation

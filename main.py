import os
from fastapi import FastAPI, UploadFile, Form, Request,File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from chatbot import get_agent , chat_with_bot
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
from pydantic import BaseModel
from resume_editor import extract_resume_info
from chatbot import extract_file_content





app = FastAPI()
agent = get_agent()
message_history = []

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("static/index.html") as f:
        return f.read()

@app.post("/edit/")
async def edit_resume(file: UploadFile, command: str = Form(...)):
    latex = (await file.read()).decode()
    # Pass user command and latex to the agent
    result = agent.run({
        "input": f"{latex},{command}"
    })
    # Save result to file to serve for download
    with open("output.tex", "w") as f:
        f.write(result)
    return {"latex": result}

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return JSONResponse({"error": "Empty message"}, status_code=400)
    # Send user message to agent and get response
    response = agent.run({"input": user_message})
    if response == "CHAT":
        response = chat_with_bot(user_message)
    print(response)
    return {"response": response}

@app.get("/download/")
def download():
    return FileResponse("output.tex", filename="edited_resume.tex", media_type="text/plain")


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    message: Optional[str] = Form(""),
):
    """
    Upload a file and optionally process it with the LLM.
    """
    try:
        # Get or create a chat session

        
        # Save the file
        file_id = f"{file.filename}"
        file_path = UPLOAD_DIR / file_id
        
        # Write file content
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            await file.seek(0)  # Reset file pointer for potential reuse
        
        # Add file reference to the chat session
        file_message = f"Uploaded file: {file.filename}"
        print(file_message)
        


        return {"message": "File uploaded successfully"}
        
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/resume_info")
def resume_info():
    resume_content = extract_file_content(os.path.join("uploads", "main.tex"))
    print(resume_content)
    resume_info = extract_resume_info(resume_content)
    return resume_info

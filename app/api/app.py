import os
from fastapi import APIRouter, HTTPException, status
from fastapi import Request, File, Form, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path
from app.services.chatbot import chat_with_bot , get_agent
from app.services.resume_editor import extract_resume_info
from app.utils.file import extract_file_content





router = APIRouter(tags=["api"])


agent = get_agent()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)



@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@router.post("/chat")
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


@router.post("/upload")
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
    

@router.get("/resume_info")
def resume_info():
    resume_content = extract_file_content(os.path.join("app/uploads", "main.tex"))

    resume_info = extract_resume_info(resume_content)
    return resume_info
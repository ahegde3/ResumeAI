import logging
from fastapi import APIRouter, HTTPException, status
from fastapi import Request, File, Form, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path
from app.services.chatbot import run_agent, clear_session_history

logger = logging.getLogger(__name__)
router = APIRouter(tags=["api"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Default session ID (can be extended to support multiple users)
DEFAULT_SESSION = "default"


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@router.post("/chat")
async def chat_endpoint(request: Request):
    """
    Process a chat message through the agent.
    """
    data = await request.json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", DEFAULT_SESSION)
    
    if not user_message:
        return JSONResponse({"error": "Empty message"}, status_code=400)
    
    try:
        # Run the agent with the user message
        response = run_agent(user_message, session_id)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/chat/clear")
async def clear_chat_history(request: Request):
    """
    Clear chat history for a session.
    """
    data = await request.json()
    session_id = data.get("session_id", DEFAULT_SESSION)
    
    try:
        clear_session_history(session_id)
        return {"message": f"Chat history cleared for session: {session_id}"}
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing history: {str(e)}"
        )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    message: Optional[str] = Form(""),
):
    """
    Upload a file and optionally process it with the LLM.
    """
    try:
        # Save the file
        file_id = f"{file.filename}"
        file_path = UPLOAD_DIR / file_id
        
        # Write file content
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            await file.seek(0)  # Reset file pointer for potential reuse
        
        logger.info(f"Uploaded file: {file.filename}")
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

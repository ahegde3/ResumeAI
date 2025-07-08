from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from chatbot import get_agent

app = FastAPI()
agent = get_agent()

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

@app.get("/download/")
def download():
    return FileResponse("output.tex", filename="edited_resume.tex", media_type="text/plain")

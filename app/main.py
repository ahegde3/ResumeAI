from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.app import router as app_router




app = FastAPI()


# Include routers
app.include_router(app_router, prefix="/api")



@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("app/static/index.html") as f:
        return f.read()



# @app.post("/edit/")
# async def edit_resume(file: UploadFile, command: str = Form(...)):
#     latex = (await file.read()).decode()
#     # Pass user command and latex to the agent
#     result = agent.run({
#         "input": f"{latex},{command}"
#     })
#     # Save result to file to serve for download
#     with open("output.tex", "w") as f:
#         f.write(result)
#     return {"latex": result}



# @app.get("/download/")
# def download():
#     return FileResponse("output.tex", filename="edited_resume.tex", media_type="text/plain")





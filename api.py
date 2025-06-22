import os
from uuid import UUID, uuid4
import threading

import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from document_processor import DocumentProcessor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

status = {}


@app.post("/verbatim")
async def process_pdf(file: UploadFile):
    task_id = uuid4()
    _, ext = os.path.splitext(file.filename)
    path = f"input/{task_id}{ext}"
    async with aiofiles.open(path, "wb") as out_file:
        await out_file.write(await file.read())
    
    status[task_id] = path

    doc = DocumentProcessor(path, "output", "verbatim")
    thread = threading.Thread(target=doc.process)
    thread.start()

    return {"tid": task_id}


@app.get("/status/{tid}")
async def pdf_status(tid: UUID):
    if tid not in status:
        raise HTTPException(status_code=404, detail="Task not found")

    if os.path.exists(f"output/{tid}.tex"):
        return {"status": "done"}
    else:
        return {"status": "processing"}

@app.get("/dl/{tid}")
async def pdf_dl(tid: UUID):
    path = f"output/{tid}.tex"
    return FileResponse(path, media_type="application/octet-stream")

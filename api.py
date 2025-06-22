from fastapi import FastAPI, UploadFile
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def actually_process(file: UploadFile):
    print(file.filename)
    RETRY_TIMEOUT = 15000
    yield {"event": "message", "retry": RETRY_TIMEOUT, "data": "what"}
    time.sleep(1)
    yield {"event": "message", "retry": RETRY_TIMEOUT, "data": "bro"}
    time.sleep(1)
    yield {"event": "end", "retry": RETRY_TIMEOUT, "data": "ok done"}


@app.post("/process")
async def process_pdf(file: UploadFile):
    return EventSourceResponse(actually_process(file))

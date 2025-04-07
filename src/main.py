import os
import logging
from typing import override
import json
from queue import Queue
import threading

import uvicorn
from dotenv import load_dotenv
import gradio as gr
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from agency_swarm.util.streaming import AgencyEventHandler
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ExampleAgency.agency import agency
from utils.demo_gradio_override import demo_gradio_override
from models.request_models import AgencyRequest, AgencyRequestStreaming
from openai.types.beta import AssistantStreamEvent


APP_TOKEN = os.getenv("APP_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
# Initialize FastAPI application
app = FastAPI()

# CORS Configuration
# For local development, allow all origins
origins = ["*"]
# For production, use specific origins:
# origins = [
#     "https://your-generated-Railway-domain.up.railway.app",  # Your Railway domain
#     "http://localhost:8000",  # Local development
# ]

# Add CORS middleware to enable cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Override the demo_gradio function
agency.demo_gradio = demo_gradio_override
# Mount the gradio interface
gradio_interface = agency.demo_gradio(agency)
app = gr.mount_gradio_app(app, gradio_interface, path="/demo-gradio", root_path="/demo-gradio")

security = HTTPBearer()

# Token verification

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token

# API endpoint

@app.post("/api/agency")
async def get_completion(request: AgencyRequest, token: str = Depends(verify_token)):
    response = agency.get_completion(
        request.message,
        message_files=request.message_files,
        recipient_agent=request.recipient_agent,
        additional_instructions=request.additional_instructions,
        attachments=request.attachments,
        tool_choice=request.tool_choice,
        verbose=request.verbose,
        response_format=request.response_format
    )
    return {"response": response}


@app.post("/api/agency-streaming")
async def get_completion_stream(request: AgencyRequestStreaming, token: str = Depends(verify_token)):
    queue = Queue()

    class StreamEventHandler(AgencyEventHandler):
        @override
        def on_event(self, event: AssistantStreamEvent) -> None:
            queue.put(event.model_dump())

        @classmethod
        def on_all_streams_end(cls):
            queue.put("[DONE]")

        @classmethod
        def on_exception(cls, exception: Exception):
            # Store the actual exception
            queue.put({"error": str(exception)})

    async def generate_response():
        try:
            def run_completion():
                try:
                    agency.get_completion_stream(
                        request.message,
                        message_files=request.message_files,
                        recipient_agent=request.recipient_agent,
                        additional_instructions=request.additional_instructions,
                        attachments=request.attachments,
                        tool_choice=request.tool_choice,
                        response_format=request.response_format,
                        event_handler=StreamEventHandler
                    )
                except Exception as e:
                    # Send the actual exception
                    queue.put({"error": str(e)})

            thread = threading.Thread(target=run_completion)
            thread.start()

            while True:
                try:
                    event = queue.get(timeout=30)
                    if event == "[DONE]":
                        break
                    # If it's an error event
                    if isinstance(event, dict) and "error" in event:
                        yield f"data: {json.dumps(event)}\n\n"
                        break
                    yield f"data: {json.dumps(event)}\n\n"
                except Queue.Empty:
                    yield f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
                    break
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    break

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global exception handler to return formatted error responses"""
    error_message = str(exc)
    if isinstance(exc, tuple):
        error_message = str(exc[1]) if len(exc) > 1 else str(exc[0])

    return JSONResponse(status_code=500, content={"error": error_message})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

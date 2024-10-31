import logging
import os
from typing import List

import uvicorn
from pydantic import BaseModel
from dotenv import load_dotenv
import gradio as gr
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ExampleAgency.agency import agency
from utils.demo_gradio_override import demo_gradio_override

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


# Models

class AttachmentTool(BaseModel):
    type: str


class Attachment(BaseModel):
    file_id: str
    tools: List[AttachmentTool]


class AgencyRequest(BaseModel):
    message: str
    attachments: List[Attachment] = []


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
        attachments=request.attachments,
    )
    return {"response": response}


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global exception handler to return formatted error responses"""
    error_message = str(exc)
    if isinstance(exc, tuple):
        error_message = str(exc[1]) if len(exc) > 1 else str(exc[0])

    return JSONResponse(status_code=500, content={"error": error_message})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

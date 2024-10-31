# Agency Swarm Railway Deployment Template

This repo demonstrates how to deploy any Agency Swarm agency as a FastAPI application in a Docker container on Railway.

## Prerequisites
* Fully tested agency
* Docker installed on your system
* Python 3.12 or higher

## Setup Instructions
1. **Add your keys:** Copy `.env.example` to `.env` and add your keys

2. **Add requirements:** Add your extra requirements to the requirements.txt file. The base requirements are:
```python:Backend/requirements.txt
agency-swarm~=0.3.1
gradio~=4.44.1
uvicorn~=0.30.1
```

3. **Add your Agency:**
   Drag-and-drop your agency into the /Backend directory and import it according to the example in the `main.py`:
```python
from ExampleAgency.agency import agency
```

4. **Set your APP_TOKEN:**
   In `Backend/main.py`, replace `YOUR_APP_TOKEN` with a secure token. This will be used for API authentication.

5. **Test your Agency:**
   Run `python agency.py` to test your agency. This will also save your agent settings in the settings.json file. Put this file in the /Backend directory. This step is necessary to avoid creating new assistants on every application start.

6. **Build and run Docker container:**
```bash
docker compose up --build
```

7. **Test API:**
```bash
# macOS/Linux
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_APP_TOKEN>" \
  -d '{"message": "What is the capital of France?"}' \
  <YOUR_DEPLOYMENT_URL>/api/agency
```

```bash
# Windows PowerShell
curl -X POST `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <YOUR_APP_TOKEN>" `
  -d "{\"message\": \"What is the capital of France?\"}" `
  <YOUR_DEPLOYMENT_URL>/api/agency
```

8. **Access the interfaces:**
   - Gradio UI: `<YOUR_DEPLOYMENT_URL>/demo-gradio`
   - API Documentation: `<YOUR_DEPLOYMENT_URL>/docs`

## API Documentation

### `POST /api/agency`

Request body:
```json
{
  "message": "What is the capital of France?",
  "attachments": [
    {
      "file_id": "file-123",
      "tools": [
        { "type": "file_search" },
        { "type": "code_interpreter" }
      ]
    }
  ]
}
```

* `message`: The message to send to the agent.
* `attachments` (optional): A list of files attached to the message, and the tools they should be added to. See [OpenAI Docs](https://platform.openai.com/docs/api-reference/messages/createMessage#messages-createmessage-attachments).

Response:
```json
{
  "response": "Paris"
}
```

### Authentication

All API requests require a Bearer token in the Authorization header:
```
Authorization: Bearer <YOUR_APP_TOKEN>
```

## Gradio Interface Features
- Dark/Light mode support
- File upload capabilities
- Support for multiple agents
- Real-time streaming responses
- Code interpreter and file search tool integration

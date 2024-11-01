# Agency Swarm Railway Deployment Template

This repo demonstrates how to deploy any Agency Swarm agency as a FastAPI application in a Docker container on Railway.

## Prerequisites

- Fully tested agency
- Docker installed is optional
- Python 3.12

## Setup Instructions

1. **Configure environment variables:**

   - For local testing: Copy `.env.example` to `.env` and add your environment variables
   - For Railway: Configure environment variables in Railway Dashboard under Variables section

2. **Add requirements:** Add your extra requirements to the `requirements.txt` file.

3. **Add your Agency:**
   Drag-and-drop your agency into the /src directory and import it according to the example in the `main.py`:

   ```python
   from ExampleAgency.agency import agency
   ```

4. **Set your APP_TOKEN:**
   In `.env`, replace `YOUR_APP_TOKEN` with a secure token. This will be used for API authentication.

5. **Add settings.json:**
   Run `python main.py` from `src/` directory, open the `http://localhost:8000/demo-gradio` and send a message. This will save your agent settings in the `settings.json` file. This step is necessary to avoid recreating assistants on every application start.

6. **Deploy on Railway:**

   1. Log into Railway
   2. Click "New Empty Project"
   3. Click "Add a service"
   4. Select "Empty service"
   5. Go to Settings
   6. Connect your repository
      - Railway will automatically detect the Dockerfile
   7. Go to Variables in Railway dashboard
   8. Add new variable:
      - `OPENAI_API_KEY`: Your OpenAI API key
      - Add any other required environment variables
   9. Click "Deploy" to start the build process
   10. Go to Settings to generate a domain:
       - Verify port is set to 8000 (it's selected automatically after deployment)
       - Click "Generate domain"

7. **Test the interfaces:**

   - Gradio UI: `<YOUR_DEPLOYMENT_URL>/demo-gradio` (local: http://localhost:8000/demo-gradio)
   - API Documentation: `<YOUR_DEPLOYMENT_URL>/docs` (local: http://localhost:8000/docs)

8. **Test API:**

   - macOS/Linux:

   ```bash
   curl -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <YOUR_APP_TOKEN>" \
    -d '{"message": "What is the capital of France?"}' \
    <YOUR_DEPLOYMENT_URL>/api/agency
   ```

   - Windows PowerShell:

   ```bash
   curl -X POST `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer <YOUR_APP_TOKEN>" `
    -d "{\"message\": \"What is the capital of France?\"}" `
    <YOUR_DEPLOYMENT_URL>/api/agency
   ```

## API Documentation

### `POST /api/agency`

Request body:

```json
{
  "message": "What is the capital of France?",
  "attachments": [
    {
      "file_id": "file-123",
      "tools": [{ "type": "file_search" }, { "type": "code_interpreter" }]
    }
  ]
}
```

- `message`: The message to send to the agent.
- `attachments` (optional): A list of files attached to the message, and the tools they should be added to. See [OpenAI Docs](https://platform.openai.com/docs/api-reference/messages/createMessage#messages-createmessage-attachments).

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

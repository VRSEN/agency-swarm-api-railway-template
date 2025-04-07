# Agency Swarm Railway Deployment Template

This repo demonstrates how to deploy any Agency Swarm agency as a FastAPI application in a Docker container on Railway.

**Video resource (watch from 13:00):**
https://youtu.be/53_e3lmk6Mo?t=810

---

## Prerequisites

- A fully tested Agency Swarm agency
- Docker installed (optional for local testing)
- Python 3.12
- Railway account
- OpenAI API key

## Setup Instructions

1. **Configure environment variables:**
   - For local testing: Copy `.env.example` to `.env` and add your environment variables.
   - For Railway: Configure environment variables in Railway Dashboard under the Variables section.

2. **Add requirements:** Add your extra requirements to the `requirements.txt` file.

3. **Add your Agency:**
   Drag-and-drop your agency into the `/src` directory and import it according to the example in `main.py` and `utils/request_models.py`.
   ```python
   from ExampleAgency.agency import agency
   ```

   Make sure your agency.py has a global agency object exposed.

4. **Set your APP_TOKEN:**
   - In `.env`, replace `YOUR_APP_TOKEN` with a secure token. This will be used for API authentication.

5. **Add settings.json:**
   - Simply run `python main.py` from the `src/` directory.
   - Open `http://localhost:8000/demo-gradio` and send a message.
   - This will save your agent settings in the `settings.json` file.
   This step is necessary to avoid recreating assistants on every application start.

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

   ## Synchronous api

   - macOS/Linux:

   ```bash
   curl -X POST \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer <YOUR_APP_TOKEN>" \
   -d '{"message": "What is the capital of France?"}' \
   <YOUR_DEPLOYMENT_URL>/api/agency
   ```

   - Windows PowerShell:
   ```
   curl -X POST `
   -H "Content-Type: application/json" `
   -H "Authorization: Bearer <YOUR_APP_TOKEN>" `
   -d "{\"message\": \"What is the capital of France?\"}" `
   <YOUR_DEPLOYMENT_URL>/api/agency
   ```

   ## Asynchronous api
   Simplest way of checking asynchronous api would be to use Curl command:

   - macOS/Linux:

   ```bash
   curl -X POST \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer <YOUR_APP_TOKEN>" \
   -d '{"message": "Write a 500 word poem"}' \
   <YOUR_DEPLOYMENT_URL>/api/agency-streaming
   ```

   - Windows PowerShell:
   ```
   curl -X POST `
   -H "Content-Type: application/json" `
   -H "Authorization: Bearer <YOUR_APP_TOKEN>" `
   -d "{\"message\": \"Write a 500 word poem?\"}" `
   <YOUR_DEPLOYMENT_URL>/api/agency-streaming
   ```

   However, since this endpoint sends raw data, in order to extract the text of the response, you can use the `test_streaming.py` script, located in the `/src` directory.

   ```
   python test_streaming.py
   ```

## API Documentation

### `POST /api/agency`

Request body:

```json
{
  "message": "What is the capital of France?",
  "message_files": ["file1.txt", "file2.pdf"],
  "verbose": false,
  "recipient_agent": "agent_name",
  "additional_instructions": "Please be concise in your response",
  "attachments": [
    {
      "file_id": "file-123",
      "tools": [{ "type": "file_search" }, { "type": "code_interpreter" }]
    }
  ],
  "tool_choice": {
    "type": "function",
    "function": { "name": "specific_function" }
  },
  
  "response_format": {
    "type": "json_object"
  }
}
```

Parameters:
- `message` (required): The message to send to the agent
- `message_files` (optional): List of file paths to include with the message. Files provided in this field would be assigned to both `file_search` and `code_interpreter` tools.
- `verbose` (optional): If true, returns intermediate messages and prints them into the console.
- `recipient_agent` (optional): Name of the specific agent to handle the request
- `additional_instructions` (optional): Extra instructions for processing the request
- `attachments` (optional): A list of files attached to the message, and the tools they should be added to. See [OpenAI Docs](https://platform.openai.com/docs/api-reference/messages/createMessage#messages-createmessage-attachments)
- `tool_choice` (optional): Specify which function should be called by the agent
- `response_format` (optional): Specify the format of the response (e.g., JSON or oai compatible response schema)

Response (verbose set to False):

```json
{
  "response": "My name is Brandon."
}
```

Response (verbose set to True):

```json
{
  "response": [
    {
      "msg_type": "text",
      "sender_name": "User",
      "receiver_name": "ExampleAgent",
      "content": "What's your name?",
      "obj": {
        "id": "msg_abc...",
        "assistant_id": null,
        "attachments": [],
        "completed_at": null,
        "content": [
          {
            "text": {
              "annotations": [],
              "value": "What's your name?"
            },
            "type": "text"
          }
        ],
        "created_at": 1742830384,
        "incomplete_at": null,
        "incomplete_details": null,
        "metadata": {},
        "object": "thread.message",
        "role": "user",
        "run_id": null,
        "status": null,
        "thread_id": "thread_abc..."
      }
    },
    {
      "msg_type": "text",
      "sender_name": "ExampleAgent",
      "receiver_name": "User",
      "content": "My name is Brandon.",
      "obj": {
        "id": "msg_abc...",
        "assistant_id": "asst_abc...",
        "attachments": [],
        "completed_at": null,
        "content": [
          {
            "text": {
              "annotations": [],
              "value": "My name is Brandon."
            },
            "type": "text"
          }
        ],
        "created_at": 1742830387,
        "incomplete_at": null,
        "incomplete_details": null,
        "metadata": {},
        "object": "thread.message",
        "role": "assistant",
        "run_id": "run_abc...",
        "status": null,
        "thread_id": "thread_abc..."
      }
    }
  ]
}
```

---

### `POST /api/agency-streaming`

Request body:

```json
{
  "message": "What is the capital of France?",
  "message_files": ["file1.txt", "file2.pdf"],
  "recipient_agent": "agent_name",
  "additional_instructions": "Please be concise in your response",
  "attachments": [
    {
      "file_id": "file-123",
      "tools": [{ "type": "file_search" }, { "type": "code_interpreter" }]
    }
  ],
  "tool_choice": {
    "type": "function",
    "function": { "name": "specific_function" }
  },
  
  "response_format": {
    "type": "json_object"
  }
}
```

Parameters:
- `message` (required): The message to send to the agent
- `message_files` (optional): List of file paths to include with the message. Files provided in this field would be assigned to both `file_search` and `code_interpreter` tools.
- `recipient_agent` (optional): Name of the specific agent to handle the request
- `additional_instructions` (optional): Extra instructions for processing the request
- `attachments` (optional): A list of files attached to the message, and the tools they should be added to. See [OpenAI Docs](https://platform.openai.com/docs/api-reference/messages/createMessage#messages-createmessage-attachments)
- `tool_choice` (optional): Specify which function should be called by the agent
- `response_format` (optional): Specify the format of the response (e.g., JSON or oai compatible response schema)

Response (a single chunk in SSE format):

```json
data: {
   "data": {
      "id": "msg_abc...", 
      "delta": {
         "content": [
            {
               "index": 0, 
               "type": "text", 
               "text": {
                  "annotations": null, 
                  "value": "Hello, "
                  }
            }
         ], 
         "role": null
      }, 
      "object": "thread.message.delta"
   }, 
   "event": "thread.message.delta"
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

## Local Docker Testing
Build and run the Docker container:

```bash
docker compose up --build
```

## Troubleshooting

- Verify all environment variables are properly set in Railway.
- Check Railway logs for any build or runtime errors.
- Ensure your settings.json is properly generated and placed in the /src directory.
- Verify your APP_TOKEN is correctly set and used in API requests.

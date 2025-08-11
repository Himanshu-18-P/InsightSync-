# No-Code Context Bot Platform

## Description

A no-code platform that lets you build and launch context-aware bots within minutes.  
Upload your content, configure prompts, and instantly create bots capable of understanding and responding based on your specific data — without writing a single line of code.

## Features

- **No-Code Setup** – Create and deploy bots without writing any code.
- **Context-Aware Responses** – Bots answer based on your uploaded documents or data.
- **Multi-Format Support** – Works with PDFs, text, and other supported formats.
- **Customizable Prompts** – Define system prompts to control bot personality and style.
- **Fast Deployment** – Launch fully functional bots in minutes.
- **Integrated LLM Support** – Compatible with Groq and other LLM APIs.
- **Persistent Storage** – Store configurations and indexes for quick reuse.


## Requirements

- **fastapi** – Web framework for building the API.
- **uvicorn** – ASGI server to run the FastAPI application.
- **python-multipart** – Handles multipart/form-data (needed for file uploads).
- **pypdf** – For reading and parsing PDF files.
- **groq** – Python SDK for interacting with Groq’s LLM API.


## Installation

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install dependencies directly
uv pip install fastapi uvicorn streamlit youtube-transcript-api python-multipart pypdf groq

# Or install from requirements file
uv pip install -r requirements.txt


## Usage

1. **Start the API Server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5000 --reload


## Usage

Open API docs:
- Swagger UI → http://localhost:5000/docs
- Redoc → http://localhost:5000/redoc

---

### Create a Bot
Send a **POST** request to `/create_bot` with:
- Bot name
- Model ID
- Groq API key
- System prompt
- Optional initial greeting line
- PDF file to index

---

### Initialize LLM
Call `/get_first_line` with the bot’s `folder_name` to set up the LLM.

---

### Chat with the Bot
Send a **POST** request to `/talk_to_bot` with:
- `folder_name`
- Your message
- Last 3 conversation messages for context

---

### Example cURL Command to Talk to Bot
```bash
curl -X POST http://localhost:5000/talk_to_bot \
  -H "Content-Type: application/json" \
  -d '{
    "folder_name": "demobot",
    "user_text": "Summarize section 2",
    "last_3_conversations": ["User: hi","Bot: hello","User: summarize"]
  }'

## API Endpoints

### `GET /model_list`
Returns available model IDs.

### `POST /create_bot` (multipart/form-data)
Create a bot and build its vector index.
- Fields: `name`, `model`, `groq_api_key`, `system_prompt`, `initial_line` (optional), `pdf` (file)

### `POST /get_first_line`
Initialize the LLM and return the bot’s initial line.
- Body: `{ "folder_name": "<slug>" }`

### `POST /talk_to_bot`
Ask a question and get an answer using retrieval + LLM.
- Body:
  ```json
  {
    "folder_name": "<slug>",
    "user_text": "Your question",
    "last_3_conversations": ["...", "...", "..."]
  }


## File Structure

├── main.py # FastAPI app entry point
├── core/ # Core logic for bot creation, indexing, and LLM processing
│ ├── init.py
│ ├── process_api.py
│ └── llm_groq.py
├── bots_data/
│ └── pdf_bots/
│ └── <folder_name>/ # Stores each bot’s config.json and original files
├── vector_store/
│ └── <folder_name>/ # Vector index data for each bot
├── requirements.txt # Python dependencies
└── README.md # Project documentation


## Example Requests

### Create a Bot
```bash
curl -X POST http://localhost:5000/create_bot \
  -F "name=DemoBot" \
  -F "model=llama-3.3-70b-versatile" \
  -F "groq_api_key=YOUR_GROQ_KEY" \
  -F "system_prompt=You are helpful." \
  -F "initial_line=Hi!" \
  -F "pdf=@/path/to/file.pdf"

# Initialize LLM
curl -X POST http://localhost:5000/get_first_line \
  -H "Content-Type: application/json" \
  -d '{"folder_name": "demobot"}'


# Talk to Bot

curl -X POST http://localhost:5000/talk_to_bot \
  -H "Content-Type: application/json" \
  -d '{
    "folder_name": "demobot",
    "user_text": "Summarize section 2",
    "last_3_conversations": ["User: hi","Bot: hello","User: summarize"]
  }'

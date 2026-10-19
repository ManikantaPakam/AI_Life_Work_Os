# AI Life & Work OS

An AI-powered personal assistant designed to help users manage everyday tasks, schedules, research, learning, and other activities through a multi-agent architecture.

The application uses a Supervisor Agent to coordinate specialized agents and a FastAPI backend to expose functionality through REST APIs.

## Key Features

- **Multi-Agent Architecture:** A Supervisor Agent delegates requests to specialized agents.
- **Task Management:** Manage personal tasks.
- **Calendar Management:** Organize events and schedules.
- **Research Assistant:** Search for information and answer questions.
- **RAG (Retrieval-Augmented Generation):** Retrieve relevant information from supported documents.
- **Email Assistant:** Support email-related workflows.
- **Long-Term Memory:** Store and retrieve supported user information.
- **Learning Assistant:** Help organize learning plans.
- **Travel Assistant:** Support travel planning.
- **Wellness Assistant:** Manage supported wellness-related information.
- **Finance Assistant:** Support finance-related workflows.
- **Conversation Persistence:** Use a LangGraph Checkpointer with PostgreSQL to preserve conversation state.

## Technology Stack

- Python
- FastAPI
- LangChain
- LangGraph
- PostgreSQL
- Pydantic
- Google Gemini
- Vector database and embedding tools used by the research/RAG implementation

## Architecture

```text
User
 |
 v
FastAPI
 |
 v
Supervisor Agent
 |
 +--> Task Agent
 +--> Calendar Agent
 +--> Research Agent
 +--> Email Agent
 +--> Memory Agent
 +--> Learning Agent
 +--> Wellness Agent
 +--> Travel Agent
 +--> Finance Agent
 |
 +--> PostgreSQL
       |
       +--> Application Data
       +--> LangGraph Checkpoints
```

## Project Structure

```text
AI_Life_Work_Os/
├── api.py
├── agents.py
├── database.py
├── config.py
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*The project structure above is illustrative. Update it to match the actual repository.*

## Prerequisites

- Python 3.12 or a compatible Python version
- PostgreSQL
- A Google Gemini API key
- Additional API credentials required by enabled integrations

## Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI_Life_Work_Os
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Set the database connection string and the API credentials required by your application.

Never commit real API keys, passwords, or other secrets.

### 5. Start the application

```bash
uvicorn api:app --reload
```

### 6. Open the API documentation

Visit:

http://127.0.0.1:8000/docs

## API

### Chat Endpoint

`POST /chat`

Example request:

```json
{
  "message": "Help me organize my tasks"
}
```

A new conversation can receive an automatically generated `thread_id`.

To continue an existing conversation, send the returned `thread_id`:

```json
{
  "message": "What did we discuss earlier?",
  "thread_id": "YOUR_EXISTING_THREAD_ID"
}
```

The application uses the configured LangGraph Checkpointer to persist conversation state.

## Environment Variables

Configure the variables required by your implementation.

Typical examples include:

- `DATABASE_URL`
- `API_ACCESS_TOKEN`
- `GOOGLE_API_KEY`

Refer to the actual configuration code and `.env.example` for the complete list.

Do not publish secret values.

## Testing

Automated testing with pytest is planned.

When the test suite is available, run it using:

```bash
pytest -v
```

## Deployment

AWS deployment is planned.

The intended deployment architecture includes:

- Amazon EC2 for the FastAPI application
- PostgreSQL for application data and conversation checkpoints
- Appropriate network security and environment configuration

## Security Notes

- Do not commit `.env` files or API keys.
- Protect endpoints using appropriate authentication and authorization.
- Restrict database network access.
- Use HTTPS for public deployments.
- Validate and test sensitive agent actions before production use.

## Future Improvements

- Automated tests using pytest
- AWS deployment
- Improved monitoring and logging
- Production-grade security and error handling
- Additional agent capabilities

## Author

Manikanta
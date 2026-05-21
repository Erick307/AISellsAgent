# WhatsApp Sales Agent

AI-powered WhatsApp sales agent built with LangGraph + Claude. Responds to customer queries, checks stock and prices from Google Drive, registers orders, and escalates to human agents when needed.

## Stack

- **FastAPI** — webhook server
- **LangGraph** — multi-agent orchestration
- **Claude (Anthropic)** — underlying LLM
- **LangSmith** — tracing and observability
- **Chatwoot** — WhatsApp integration and conversation UI
- **PostgreSQL** — checkpointing and order storage
- **Google Drive** — stock and price data source

## Project Structure

```
app/
├── main.py                  # FastAPI entry point
├── config.py                # Settings from .env
├── agents/                  # LangGraph graph and agent nodes
├── tools/                   # Agent tools (Drive, database)
├── prompts/                 # ChatPromptTemplate YAML files
├── webhooks/                # Chatwoot webhook handler
├── services/                # Chatwoot API client, DB connection
└── models/                  # Pydantic schemas
```

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in all values:
   ```bash
   cp .env.example .env
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Updating agent prompts

Edit the relevant YAML file in `app/prompts/`, commit, and restart the server.

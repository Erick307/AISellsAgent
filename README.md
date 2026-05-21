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

1. Install dependencies with [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```

2. Start the full stack (Postgres + Redis + Chatwoot) via Docker:
   ```bash
   docker-compose up -d
   ```
   - Chatwoot UI: http://localhost:3000
   - Postgres: localhost:5432
   - Redis: localhost:6379

3. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

4. Run the agent server:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   - Agent API: http://localhost:8000
   - Health check: http://localhost:8000/health

## Testing with ngrok

Use [ngrok](https://ngrok.com) to expose your local server so Chatwoot can reach your webhook (required for WhatsApp testing):

```bash
# Install ngrok (once)
brew install ngrok

# Expose the local agent server
ngrok http 8000
```

Copy the `https://xxxx.ngrok.io` URL and set it as the webhook URL in Chatwoot:
- Chatwoot → Settings → Integrations → Webhooks → New Webhook
- URL: `https://xxxx.ngrok.io/webhooks/chatwoot`
- Events: ✅ Message Created

## Updating agent prompts

Edit the relevant YAML file in `app/prompts/`, commit, and restart the server.

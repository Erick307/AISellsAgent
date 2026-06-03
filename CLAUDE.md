# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the server (dev mode)
uv run uvicorn app.main:app --reload

# Run the graph directly (no Chatwoot needed)
uv run python test_graph.py

# Run tests
uv run pytest

# Expose local server to Chatwoot via ngrok
ngrok http 8000
```

Start the infrastructure (Postgres, Redis, Chatwoot) before running the server:
```bash
docker-compose up -d
```

## Architecture

This is a **multi-agent WhatsApp sales bot**: Chatwoot receives WhatsApp messages → forwards them via webhook → FastAPI runs a LangGraph graph → reply is sent back through the Chatwoot API.

### Request flow

1. **`app/webhooks/chatwoot.py`** — receives `POST /webhooks/chatwoot`. Verifies signature, debounces rapid messages (configurable `message_debounce_seconds`), checks if conversation is escalated (human still active → bot stays silent). After debounce, invokes the graph asynchronously and sends the result back via `send_message()`.

2. **`app/agents/graph.py`** — builds and holds the LangGraph `StateGraph`. The singleton `graph_manager` (initialized at FastAPI startup) owns the Postgres checkpointer connection. Thread ID = customer phone number, so each customer has its own persisted conversation state.

3. **Agent nodes** (`app/agents/`):
   - **`orchestrator`** — called first every turn. Uses `claude-sonnet-4-6` with structured output (`RouteDecision`) to decide: reply directly and `end`, or route to `stock_catalog`, `order`, or `escalation`. If the last message is already an AI reply, it skips the LLM call and ends immediately (avoids Anthropic rejection of assistant-ending conversations).
   - **`stock_catalog`** — runs a tool loop against Google Drive tools to answer stock/price queries, then returns to orchestrator.
   - **`order`** — runs a tool loop against database tools to register confirmed orders, then returns to orchestrator.
   - **`escalation`** — calls `interrupt()` to pause the graph (state saved in Postgres), opens the Chatwoot conversation for a human. Bot resumes after `escalation_resume_hours` of human inactivity.

4. **`app/agents/state.py`** — `AgentState` is the shared TypedDict: `messages` (full history), `conversation_id`, `customer_phone`, `next_agent`, `escalated_at`.

### Prompts

Each agent loads its prompt from a YAML file in `app/prompts/` via `load_prompt(name)`. To change agent behavior, edit the relevant YAML and restart the server — no code changes needed.

### Tools (currently stubs)

- `app/tools/drive.py` — `search_drive` (Google Drive lookup, stub)
- `app/tools/database.py` — `register_order`, `register_unmet_demand` (DB writes, stubs)

Real implementations are the main pending work.

### Key config (`app/config.py`)

All settings come from `.env` (see `.env.example`). Notable:
- `POSTGRES_URL` — must use `postgresql+asyncpg://` scheme; the graph internally strips the dialect prefix for psycopg.
- `MESSAGE_DEBOUNCE_SECONDS` — how long to wait before processing a message (coalesces rapid typing).
- `ESCALATION_RESUME_HOURS` — hours of human silence before the bot takes back the conversation.

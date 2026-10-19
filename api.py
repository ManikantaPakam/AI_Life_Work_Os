"""FastAPI entry point for the existing AI Life & Work OS project.

Keeps the existing create_agent() architecture and existing tools unchanged.
No email approval/rejection endpoints are implemented.
"""

from contextlib import asynccontextmanager
import logging
import os
import secrets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from agents import build_agents
from database import get_connection, initialize_database
import uuid
from config import DATABASE_URL
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("lifeos.api")
bearer_scheme = HTTPBearer(auto_error=False)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class ChatResponse(BaseModel):
    response: str
    thread_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize PostgreSQL, checkpointer, and agents."""
    logger.info("Starting AI Life & Work OS API")

    initialize_database()

    checkpoint_pool = ConnectionPool(
        conninfo=DATABASE_URL,
        min_size=1,
        max_size=10,
        kwargs={
            "autocommit": True,
            "row_factory": dict_row,
        },
        open=False,
    )

    try:
        checkpoint_pool.open(wait=True)

        checkpointer = PostgresSaver(checkpoint_pool)

        # Create or migrate the checkpointer tables.
        checkpointer.setup()

        app.state.checkpointer_pool = checkpoint_pool
        app.state.checkpointer = checkpointer

        # Reuse the existing Supervisor and specialist agents.
        app.state.agents = build_agents(
            checkpointer=checkpointer
        )

        logger.info(
            "Database, checkpointer, and agents initialized"
        )

        yield

    finally:
        checkpoint_pool.close()
        logger.info("PostgreSQL checkpointer pool closed")
        logger.info("Stopping AI Life & Work OS API")


app = FastAPI(
    title="AI Life & Work OS API",
    description=(
        "REST API for the existing AI Life & Work OS Supervisor Agent. "
        "Existing specialist agents and tools are reused without adding email HITL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def require_api_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    """Require a configured bearer token for chat requests."""
    expected_token = os.getenv("API_ACCESS_TOKEN", "").strip()
    if not expected_token:
        logger.error("API_ACCESS_TOKEN is not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API access token is not configured on the server.",
        )

    if credentials is None or not secrets.compare_digest(
        credentials.credentials, expected_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_response_text(result: dict) -> str:
    """Extract the final message from the existing supervisor result."""
    messages = result.get("messages", [])
    if not messages:
        return "No response generated."

    content = getattr(messages[-1], "content", "")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = [
            str(part.get("text", ""))
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        ]
        if text_parts:
            return "\n".join(text_parts)

    return str(content)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic liveness check."""
    return {"status": "ok", "application": "AI Life & Work OS"}


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    """Check that PostgreSQL is reachable."""
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
        return {"status": "ready", "database": "ok"}
    except Exception:
        logger.exception("Readiness check failed: PostgreSQL unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application dependencies are not ready.",
        )


@app.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[Depends(require_api_token)],
)
def chat(request: ChatRequest) -> ChatResponse:
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(
            status_code=422,
            detail="Message must not be empty.",
        )

    thread_id = request.thread_id or str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        result = app.state.agents["supervisor"].invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ]
            },
            config=config,
        )

        return ChatResponse(
            response=extract_response_text(result),
            thread_id=thread_id,
        )

    except Exception:
        logger.exception("Supervisor agent request failed")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request.",
        )
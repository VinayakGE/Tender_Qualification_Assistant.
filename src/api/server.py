"""FastAPI application factory for the Tender Qualification Assistant."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.utils.config import get_config
from src.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler.

    Runs startup tasks before the app begins serving requests,
    and cleanup tasks on shutdown.
    """
    config = get_config()
    configure_logging(level=config.LOG_LEVEL)

    logger.info(
        "server_starting",
        model=config.MODEL,
        incoming_dir=str(config.INCOMING_DIR),
        ledger_file=str(config.LEDGER_FILE),
    )

    # Ensure required directories exist
    from src.utils.helpers import ensure_dir
    ensure_dir(config.INCOMING_DIR)
    ensure_dir(config.RAW_DIR)
    ensure_dir(config.PARSED_DIR)
    ensure_dir(config.OUTCOMES_DIR)
    ensure_dir(config.COMPANY_PROFILES_DIR)

    yield

    logger.info("server_shutting_down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.
    """
    app = FastAPI(
        title="Tender Qualification Assistant",
        description=(
            "Decision intelligence for government procurement. "
            "Analyze tender PDFs and receive a BID / REVIEW / NO BID recommendation."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS — allow all origins in development; restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="")

    return app


# Module-level app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    configure_logging(level=config.LOG_LEVEL)

    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

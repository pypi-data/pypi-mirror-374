from contextlib import asynccontextmanager
import sys
from fastapi import FastAPI
from loguru import logger
import logging
import uvicorn

from vrouter_agent.core.db import init_db
from vrouter_agent.api import orders, transactions, tunnel_config, telemetry, root
from vrouter_agent.services.chain import Chain
from vrouter_agent.services.startup import initialize_services, shutdown_services
from vrouter_agent.utils.logger import InterceptHandler, format_record
import os
from vrouter_agent.core.config import settings
LOG_FILE = "/var/log/vrouter-agent.log"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.debug("Initializing database")
    init_db()
    
    # Initialize application services (stream listener, processor, etc.)
    logger.info("Initializing application services...")
    success = await initialize_services()
    if not success:
        logger.error("Failed to initialize application services")
        sys.exit(1)
    
    for route in app.routes:
        logger.info(f"Route: {route.path} - {route.name}")

    yield
    
    # Shutdown
    logger.info("Shutting down application services...")
    await shutdown_services()

app = FastAPI(
    title="VRouter Agent API",
    description="API for VRouter tunnel configuration and telemetry monitoring",
    version="1.0.0",
    contact={
        "name": "USDN vRouter Agent Server",
        "email": "support@usdatanetworks.com",
    },
    license_info={
        "name": "Private License",
    },
    lifespan=lifespan
)
app.include_router(root.router, tags=["root"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(tunnel_config.router, tags=["tunnel-config"])
app.include_router(telemetry.router, tags=["telemetry"])


# set loguru format for root logger
logging.getLogger().handlers = [InterceptHandler()]

# set format
logger.configure(
    handlers=[
        {"sink": sys.stdout, "level": logging.DEBUG, "format": format_record},
        {
            "sink": LOG_FILE,
            # "rotation": "1 MB",
            # "compression": "zip",
            # "enqueue": True,
            # "backtrace": True,
            "level": logging.INFO,
            "format": format_record,
        },
    ]
)




def start():

    logger.info("Starting vRouter Agent Server...")
    logger.info("************************")

    # Get host from environment variable with fallback
    host = os.getenv("VRouterAgentHost", "127.0.0.1")  # Default to localhost instead of 0.0.0.0
    port = int(os.getenv("VRouterAgentPort", "8000"))
    logger.info(f"Log file is saved to {LOG_FILE}")
    logger.info(f"Starting server on {host}:{port}")
    logger.info("************************")
    logger.info(settings.config.interfaces)
    logger.info(settings.config.multichain)
    
    # Basic multichain connectivity check - stream subscription for hostname and order_update is handled by startup services
    chain = Chain(chain=settings.config.multichain.chain, user=settings.config.global_.user)
    if not chain.is_running():
        logger.error(f"Multichain daemon for chain {settings.config.multichain.chain} is not running.")
        sys.exit(1)
    logger.info("Multichain daemon is running")
    
    uvicorn.run(
        "vrouter_agent.main:app", 
        host=host,
        port=port,
        reload=True,
        log_level="debug",    
    )

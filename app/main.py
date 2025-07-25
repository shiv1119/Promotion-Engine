from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes import router
from services.loader import load_rules_from_yaml
from core.config import RULE_FILE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Loading rules from YAML file...")
        load_rules_from_yaml(RULE_FILE)
        logger.info("Rule loading completed.")
    except Exception as e:
        logger.error(f"Failed to load rules during startup: {e}")
        raise e
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title="Promotion Rule‑Engine Microservice",
    version="1.0.0",
    description="A flexible, rule-based promotion engine for game players.",
    lifespan=lifespan,
    docs_url="/",           
    redoc_url=None,         
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1, 
        "docExpansion": "none",         
        "displayRequestDuration": True,  
    },
    swagger_ui_init_oauth={},
)


# Here we register API routes
app.include_router(router, prefix="/api", tags=["Promotion API"])

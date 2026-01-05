from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.app_logs import configure_logging, LogLevels
from src.config.app_config import app_config
from src.adapters.routes.health_routes import health_router
from src.adapters.routes.order_routes import order_router

configure_logging(LogLevels.info.value)


def create_application() -> FastAPI:
    app = FastAPI(
        title=app_config.api_title,
        version=app_config.api_version,
        description=app_config.api_description,
        prefix=app_config.api_prefix,
    )

    app.add_middleware(CORSMiddleware, **app_config.cors_config)
    app.include_router(router=health_router)
    app.include_router(router=order_router)
    return app


app = create_application()

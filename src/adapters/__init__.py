# Interface Adapters Layer
# This layer handles external concerns like HTTP, databases, and data formatting

from .routes.health_routes import health_router
from .di.container import Container, container
from .presenters.implementations.json_presenter import JSONPresenter

__all__ = [
    "health_router",
    "Container",
    "container",
    "JSONPresenter",
]

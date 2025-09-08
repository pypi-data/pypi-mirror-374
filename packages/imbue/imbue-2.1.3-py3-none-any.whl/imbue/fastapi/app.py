from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, AsyncIterator, Callable, TypedDict

from imbue.container import Container
from imbue.contexts.application import ApplicationContainer


class State(TypedDict):
    app_container: ApplicationContainer


def app_lifespan(container: Container) -> Callable[[Any], AsyncContextManager[State]]:
    @asynccontextmanager
    async def _lifespan(_) -> AsyncIterator[State]:
        """Initializes the application container.
        This should be passed to the `lifespan` init parameter of FastAPI.
        For more details, see
            - https://fastapi.tiangolo.com/advanced/events
            - https://www.starlette.io/lifespan/.
        """
        async with container.application_context() as app_container:
            yield {"app_container": app_container}

    return _lifespan

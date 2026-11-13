from fastapi import FastAPI

from fitness_intelligence.api.health import router


def create_app() -> FastAPI:
    app = FastAPI(title="Fitness Intelligence", version="0.1.0")
    app.include_router(router)
    return app


app = create_app()

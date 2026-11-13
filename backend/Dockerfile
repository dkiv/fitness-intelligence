FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
COPY tests ./tests
RUN uv sync --frozen --group dev
EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "fitness_intelligence.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

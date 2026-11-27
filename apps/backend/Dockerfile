FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-build
COPY apps/backend apps/backend
COPY migrations migrations
COPY alembic.ini .
ENV PYTHONPATH=/app/apps/backend
ENV UV_CACHE_DIR=/tmp/uv-cache
RUN useradd --create-home app && chown -R app:app /app
USER app
CMD ["uv", "run", "--no-sync", "uvicorn", "hr_ops.api:app", "--host", "0.0.0.0", "--port", "8000"]

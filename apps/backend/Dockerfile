FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev
COPY apps/backend apps/backend
COPY migrations migrations
COPY alembic.ini .
ENV PYTHONPATH=/app/apps/backend
CMD ["uv", "run", "--no-sync", "uvicorn", "hr_ops.api:app", "--host", "0.0.0.0", "--port", "8000"]

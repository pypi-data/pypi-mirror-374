FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock main.py ./

RUN uv sync

CMD ["uv", "run", "main.py"]
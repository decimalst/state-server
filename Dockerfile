# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ Stage 1: Base image + Poetry installation                                    │
# └──────────────────────────────────────────────────────────────────────────────┘
FROM python:3.13-slim AS base

# Prevent Python from buffering stdout/stderr (so logs appear immediately)
ENV PYTHONUNBUFFERED=1

# Install curl (needed to fetch Poetry’s installer) and build-essential 
# (for any C extensions that Shapely may need)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry (we pin a known‐good version here; you can bump as needed)
RUN curl -sSL https://install.python-poetry.org | python3 - --version 2.1.3 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ Stage 2: Copy lockfiles + src folder, install deps                           │
# └──────────────────────────────────────────────────────────────────────────────┘
FROM base AS builder

WORKDIR /app

# 1) Copy pyproject.toml & poetry.lock first (cache dependencies)
COPY pyproject.toml poetry.lock README.md /app/

# 2) Copy src/ so Poetry can see your 'state_server' package itself
COPY src/ ./src

# Configure Poetry to install system-wide, then install “regular” dependencies + the package itself
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ Stage 3: Final runtime image                                                 │
# └──────────────────────────────────────────────────────────────────────────────┘
FROM python:3.13-slim AS final

ENV PYTHONUNBUFFERED=1

# (Optional) create a non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
USER appuser

# Copy everything under /usr/local (so site-packages + all console-scripts like uvicorn)
COPY --from=builder /usr/local /usr/local

# Copy your full project (including src/, files/, tests/, etc.)
COPY --chown=appuser:appuser . /home/appuser/app

EXPOSE 8080

# ── Notice the “--app-dir src” flag, pointing Uvicorn at `src/` for the 'state_server' package ──
CMD ["uvicorn", "state_server.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--app-dir", "src"]
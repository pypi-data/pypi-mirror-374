# ====== Build stage ======
FROM mirror.gcr.io/astral/uv:0.8-python3.13-alpine AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Prefer the system python
ENV UV_PYTHON_PREFERENCE=only-system

# Copy the required files first
COPY pyproject.toml uv.lock .

# Install system dependencies and Python package manager
RUN apk update && \
    apk add --no-cache --virtual .build-deps \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo

# Install the project's dependencies using the lockfile and settings
RUN uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . .
RUN uv build && uv pip install dist/*.whl

# ====== Production build ======
FROM public.ecr.aws/docker/library/python:3.13-alpine

# Place executables in the environment at the front of the path and include other binaries
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Install runtime dependencies and create application user
RUN apk update && \
    apk add --no-cache ca-certificates && \
    update-ca-certificates && \
    addgroup -S app && \
    adduser -S app -G app -h /app

# Copy application artifacts from build stage
COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Run as non-root
USER app

ENTRYPOINT ["tinyurl-mcp"]

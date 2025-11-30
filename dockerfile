# ============================================================
# HB-Eval System – Open-Core Edition
# Official Docker Image (Multi-stage build for optimal size)
# Python 3.11 Slim → ~85 MB base image
# ============================================================

# ──────── Stage 1: Builder ────────
FROM python:3.11-slim AS builder

# Performance optimization + prevent cache
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (leverage Docker cache)
COPY pyproject.toml setup.py setup.cfg README.md ./
COPY hb_eval ./hb_eval

# Install dependencies + package
RUN pip install --upgrade pip setuptools wheel && \
    pip install .

# ──────── Stage 2: Runtime (Minimal final image) ────────
FROM python:3.11-slim

# Create non-root user (security best practice)
RUN useradd --create-home --shell /bin/bash hbuser

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build/hb_eval ./hb_eval

# Copy additional project files
COPY README.md LICENSE ./
COPY papers ./papers
COPY tasks ./tasks

# Switch to non-root user
USER hbuser

# Environment variable for production mode
ENV HB_EVAL_MODE=production \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import hb_eval; print('OK')" || exit 1

# Labels for metadata
LABEL maintainer="hbevalframe@gmail.com" \
      version="1.0.0" \
      description="HB-Eval System Open-Core Edition" \
      org.opencontainers.image.source="https://github.com/hb-evalSystem/HB-System"

# Default command: run demo
CMD ["python", "-m", "hb_eval.demo"]

# Alternative: Interactive shell
# CMD ["python", "-i", "-c", "from hb_eval import *; print('HB-Eval System ready!')"]

# HuggingFace Spaces (Docker SDK) build target.
#
# Hosts the qrouter HTTP wrapper at https://lkempe-qrouter.hf.space.
# Builds with the QNLP stack so BACKEND="lambeq" — meridian-vm only ever
# runs the stub mode (or no qrouter at all once we move to the Worker
# proxy in front of this Space).
#
# Note: HF builds get generous CPU + 16 GB RAM, so the lambeq + torch
# install is fine here even though it would crater the meridian-vm.

FROM python:3.12-slim

# System deps for spaCy / lambeq (curl is for diagnostics).
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install runtime + QNLP deps. CPU torch only; HF Spaces CPU has no GPU.
RUN pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch \
 && pip install --no-cache-dir \
        fastapi uvicorn numpy scipy \
        lambeq pennylane jax

# Source last so iterating on application code is a fast layer.
COPY src/ ./src/
COPY pyproject.toml ./

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV QROUTER_HOST=0.0.0.0
ENV QROUTER_PORT=7860

EXPOSE 7860

CMD ["uvicorn", "qrouter.http_server:app", "--host", "0.0.0.0", "--port", "7860", "--app-dir", "/app/src"]

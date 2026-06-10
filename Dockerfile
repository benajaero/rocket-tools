FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy package manifest and source
COPY pyproject.toml .
COPY src ./src

# Install production dependencies
RUN pip install --no-cache-dir -e .

# Expose ASGI port
EXPOSE 8000

# Run the MCP SSE server
CMD ["uvicorn", "rocket_tools.asgi:app", "--host", "0.0.0.0", "--port", "8000"]

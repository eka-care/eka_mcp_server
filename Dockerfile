# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Add your code (if needed)
# COPY . /app
# WORKDIR /app

#install dependencies via uv
# RUN uv pip install -r pyproject.toml

# Define the default command
CMD ["run_eka_mcp_server"]
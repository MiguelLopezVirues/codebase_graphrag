# infra/aws/graph_builder/Dockerfile
FROM public.ecr.aws/lambda/python:3.12

# Install UV for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# # Install system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     unzip \
#     curl \
#     # remove installation files and metadata
#     && rm -rf /var/lib/apt/lists/* 

# # Install AWS CLI
# RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
#     unzip awscliv2.zip && \
#     ./aws/install && \
#     # Remove installation files to reduce image size
#     rm -rf awscliv2.zip aws

COPY pyproject.toml uv.lock ./

# Create and activate a virtual environment using uv
RUN uv venv .venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:${PYTHONPATH:-}"

RUN uv sync

COPY src/ ./src/
RUN rm -rf ./src/rag
COPY test/ ./test/

COPY infra/aws/graph_builder/entrypoint.sh ./

CMD ["src.database.graph_database_builder.lambda_handler"]
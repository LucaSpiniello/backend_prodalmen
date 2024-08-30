# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /codigo_proyecto

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz-dev \
    libgraphviz-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requerimientos.txt /codigo_proyecto/
RUN pip install --upgrade pip && pip install -r requerimientos.txt

# Copy project files
COPY . /codigo_proyecto/

# Copy and set entrypoint
COPY entrypoint.sh /codigo_proyecto/entrypoint.sh
RUN chmod +x /codigo_proyecto/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/codigo_proyecto/entrypoint.sh"]

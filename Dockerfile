FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create output directory for caching profiles
RUN mkdir -p output

# Expose port (Railway will provide this via PORT env)
EXPOSE 8000

# Start command
CMD ["python", "-m", "src.server"]

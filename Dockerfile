FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/
COPY .env* ./

# Set Python path
ENV PYTHONPATH=/app

# Create a non-root user
RUN useradd -m -u 1000 taskagent && chown -R taskagent:taskagent /app
USER taskagent

# Default command
CMD ["python", "-m", "src.main"]
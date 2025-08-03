# Dockerfile for Cloud Run deployment (alternative to Cloud Functions)
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
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Create a simple HTTP server wrapper for Cloud Run
RUN echo 'from flask import Flask, request\n\
import functions_framework\n\
from src.main_digest import main_function_digest\n\
from cloudevents.http import CloudEvent\n\
\n\
app = Flask(__name__)\n\
\n\
@app.route("/", methods=["POST"])\n\
def handle_request():\n\
    # Convert HTTP request to CloudEvent\n\
    event = CloudEvent({"type": "manual", "source": "cloud-run"}, request.get_json())\n\
    main_function_digest(event)\n\
    return "OK", 200\n\
\n\
if __name__ == "__main__":\n\
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))' > app.py

# Install Flask for Cloud Run
RUN pip install flask

# Run the application
CMD ["python", "app.py"]
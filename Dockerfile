# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY templates/ ./templates/
COPY static/ ./static/

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "backend/app.py"]

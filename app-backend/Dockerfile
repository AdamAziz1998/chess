# Use a lightweight, secure Python 3.11 slim image
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk
# Ensure console output is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root group and user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install system dependencies if required, and Python dependencies
# --no-cache-dir keeps the image size small by avoiding locally caching packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Change ownership of the /app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user for enhanced security
USER appuser

# Expose port 8000 which will be used by FastAPI/uvicorn
EXPOSE 8000

# Start the application using uvicorn, ensuring it binds to all interfaces (0.0.0.0)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

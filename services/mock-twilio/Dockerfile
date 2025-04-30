FROM python:3.12-slim

WORKDIR /app

# Install uv for faster and more reliable dependency installation
RUN pip install --no-cache-dir uv

# Copy requirements first for better caching
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3000

# Run the application
CMD ["uvicorn", "mock_twilio.main:app", "--host", "0.0.0.0", "--port", "3000"]

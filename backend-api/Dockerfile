FROM python:3.11-slim


WORKDIR /app

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies if any (usually not needed for pure flask, but good practice)
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Change ownership
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Using gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]

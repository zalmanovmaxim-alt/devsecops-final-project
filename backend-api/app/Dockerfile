FROM python:3.11-slim


WORKDIR /app

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies if any (usually not needed for pure flask, but good practice)
# RUN apt-get update && apt-get install -y ...

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Change ownership
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Using gunicorn is better for production, but main.py has app.run()? 
# The user wants "Working Flask API". python main.py is fine, but gunicorn is better.
# However, requirements.txt doesn't have gunicorn. I should add it or use python main.py.
# Prompt says "DecSecOps", so I'll stick to python main.py to avoid changing too much logic, 
# or add gunicorn to requirements?
# Let's run it as python main.py for compatibility with existing code structure.
CMD ["python", "main.py"]

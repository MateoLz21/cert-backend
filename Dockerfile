FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for psycopg.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage layer caching.
COPY requirements/ requirements/
ARG REQUIREMENTS=requirements/development.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ${REQUIREMENTS}

# Copy project source.
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

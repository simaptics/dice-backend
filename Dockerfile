FROM public.ecr.aws/docker/library/python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Django project
COPY project /app/project

# Switch to Django project dir
WORKDIR /app/project

EXPOSE 8500

CMD ["gunicorn", "dice_backend.wsgi:application", "--bind", "0.0.0.0:8500"]
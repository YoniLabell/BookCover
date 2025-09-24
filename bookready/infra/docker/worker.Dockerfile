FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libqpdf-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libtiff5 \
        liblcms2-dev \
        libffi-dev \
        ghostscript \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app /app/app

CMD ["python", "app/workers/worker.py"]

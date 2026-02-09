FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

RUN mkdir -p data/cache data/pdfs data/exports data/uploads data/logs

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=epstein_enhanced.web.app

CMD ["flask", "run", "--host=0.0.0.0"]

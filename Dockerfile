FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SIGNALROOM_DATA_DIR=/app/data/runtime

WORKDIR /app

COPY pyproject.toml ./
COPY signalroom ./signalroom
RUN pip install --no-cache-dir .

COPY index.html app.js styles.css ./

EXPOSE 8000

CMD ["sh", "-c", "python -m signalroom.training && uvicorn signalroom.main:app --host 0.0.0.0 --port 8000"]


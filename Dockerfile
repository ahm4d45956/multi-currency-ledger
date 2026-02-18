FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY ledger-service/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the service
COPY ledger-service/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
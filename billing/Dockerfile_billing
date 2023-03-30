FROM python:3.10.9-slim

WORKDIR /billing
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
# COPY ./ssl .
COPY . .
CMD ["python", "-m", "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornH11Worker", "--bind", "0.0.0.0:443", "--workers", "1", "--keyfile", "private_key.pem", "--certfile", "certificate.pem"]
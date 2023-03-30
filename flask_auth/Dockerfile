FROM python:3.10.9-slim
WORKDIR /flask_auth
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--log-level", "DEBUG", "--reload"]

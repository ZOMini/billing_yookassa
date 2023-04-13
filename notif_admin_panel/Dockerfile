FROM python:3.10.9-slim

WORKDIR /admin_notif

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .

RUN mkdir -p /admin_notif/static/ \
     && mkdir -p /admin_notif/scripts/ \
     && pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY /. .
COPY /scripts ./scripts
COPY script.py .

EXPOSE 8000

CMD ["gunicorn", "admin_notif.wsgi", "--bind", "0.0.0.0:8082"]
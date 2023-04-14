FROM python:3.10.9-slim

WORKDIR /billing_admin

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .

RUN mkdir -p /billing_static_volume/static/ \
     && mkdir -p /billing_static_volume/scripts/ \
     && pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY /. .

EXPOSE 8202

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8202"]
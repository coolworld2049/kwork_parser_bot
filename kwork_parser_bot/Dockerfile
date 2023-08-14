FROM python:3.11

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY kwork_parser_bot /app

COPY prisma /app

COPY prestart.sh /app/prestart.sh

COPY start.sh /app/start.sh

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

ENTRYPOINT  ["bash", "./start.sh"]

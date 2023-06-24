FROM python:3.11

COPY kwork_parser_bot/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt -U

COPY kwork_parser_bot /app

RUN chmod +x /app/prestart.sh && chmod +x /app/start.sh

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

EXPOSE 80

ENTRYPOINT  ["bash", "./start.sh"]

FROM python:3.11

COPY kwork_parser_bot/requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY kwork_parser_bot /app

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

EXPOSE 80

ENTRYPOINT  ["bash", "./start.sh"]

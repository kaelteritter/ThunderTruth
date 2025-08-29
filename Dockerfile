FROM python:3.12-alpine

RUN adduser -D -s /bin/sh player
USER player

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=player:player . .

CMD ["python", "-m", "core.main"]
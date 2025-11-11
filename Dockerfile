FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://tailscale.com/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir aiohttp

COPY main.py .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]

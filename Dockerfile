# Dockerfile

FROM python:3.11-slim-bookworm

WORKDIR /app

COPY . /app
RUN chmod +x /app/entrypoint.sh

RUN pip install --no-cache-dir -r requirements.txt

# Run entrypoint.sh when the container launches
ENTRYPOINT ["/app/entrypoint.sh"]


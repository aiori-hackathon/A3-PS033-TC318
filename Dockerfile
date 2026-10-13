FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY src /app/src
EXPOSE 8443
CMD ["uvicorn", "src.services.app:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-certfile", "/run/certs/server.crt", "--ssl-keyfile", "/run/certs/server.key"]

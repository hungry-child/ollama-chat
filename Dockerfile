# Dockerfile
FROM python:3.9-slim
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY app.py /app/
COPY templates/chat.html /app/templates/chat.html
WORKDIR /app
CMD ["python", "app.py"]

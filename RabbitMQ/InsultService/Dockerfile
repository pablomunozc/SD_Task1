FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY InsultService.py .

ENV RABBITMQ_HOST=rabbitmq
ENV REDIS_HOST=redis

CMD ["python", "InsultService.py"]
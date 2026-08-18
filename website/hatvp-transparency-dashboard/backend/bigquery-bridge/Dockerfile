FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY main.py query.py service.py ./

ENV PORT=8080
CMD ["sh", "-c", "exec functions-framework --target=dashboard --source=main.py --port=${PORT:-8080}"]

FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install-deps
RUN playwright install chromium
# RUN pip install playwright
# RUN pip install langchain-ollama

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

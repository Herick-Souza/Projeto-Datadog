FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# ddtrace-run instrumenta Flask e SQLite automaticamente
CMD ["ddtrace-run", "gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]

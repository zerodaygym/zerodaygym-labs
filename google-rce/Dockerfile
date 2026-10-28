FROM python:3.11-slim

RUN useradd -r -u 1000 devsite
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
COPY flag.txt /flag.txt
RUN chmod 444 /flag.txt

USER devsite
EXPOSE 8080
# --preload: the OAuth client secret is generated once and shared by all workers
CMD ["gunicorn", "--preload", "-w", "2", "--threads", "4", "-b", "0.0.0.0:8080", "--access-logfile", "-", "app:app"]

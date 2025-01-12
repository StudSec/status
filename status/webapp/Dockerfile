FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the rest
COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["waitress-serve", "--host", "0.0.0.0", "app:app"]
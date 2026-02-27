FROM python:3.11

# Cài netcat để chờ DB
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Đảm bảo Python tìm thấy package app
ENV PYTHONPATH=/app

ENTRYPOINT ["/entrypoint.sh"]
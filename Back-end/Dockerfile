FROM python:3.12-slim-bookworm

WORKDIR /app

ENV SB_SKIP_BROWSER_INSTALL=1
ENV SELENIUMBASE_NO_BROWSER_INSTALL=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin

# Install Chrome + tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD python manage.py migrate && python manage.py collectstatic --no-input && daphne -p $PORT -b 0.0.0.0 core.asgi:application
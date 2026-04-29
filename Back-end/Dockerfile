FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

ENV SB_SKIP_BROWSER_INSTALL=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV SELENIUMBASE_NO_BROWSER_INSTALL=1

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y tesseract-ocr

COPY . .

EXPOSE 10000

CMD python manage.py migrate && python manage.py collectstatic --no-input && daphne -p $PORT -b 0.0.0.0 core.asgi:application
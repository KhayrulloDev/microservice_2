# FastAPI va Telegram bot uchun asosiy Python 3.8
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

# Zarur kutubxonalarni o'rnatish
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani ishga tushirish uchun barcha fayllarni nusxalash
COPY . /app

# FastAPI va Telegram botni ishga tushirish
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8001  --reload"]

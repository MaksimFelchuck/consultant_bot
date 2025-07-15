FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install watchfiles

# Остальной код будет монтироваться через volume

CMD ["watchfiles", "python src/bot.py"] 
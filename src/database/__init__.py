from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Получаем строку подключения из переменной окружения или задаём вручную
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/consultant_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine) 
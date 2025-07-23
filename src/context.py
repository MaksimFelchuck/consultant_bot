import json
import logging
import os
from pathlib import Path

from config import DEFAULT_CONTEXT
from repository import category_repo

CONTEXT_FILE = Path(__file__).parent / "context.txt"


class ContextManager:
    def __init__(self):
        self.context = DEFAULT_CONTEXT
        self.load_context()

    def load_context(self):
        # Загружаем базовый контекст
        if CONTEXT_FILE.exists():
            with CONTEXT_FILE.open("r", encoding="utf-8") as f:
                base_context = f.read()
            logging.info(
                f"[ТехноМаркет] Изначальный контекст для бота загружен из context.txt."
            )
        else:
            base_context = DEFAULT_CONTEXT
            logging.info(
                f"[ТехноМаркет] Файл context.txt не найден, используется контекст по умолчанию."
            )

        # Заменяем плейсхолдер категориями из БД
        try:
            categories = category_repo.get_all()
            if categories:
                categories_list = ", ".join([cat.name.lower() for cat in categories])
                self.context = base_context.format(categories_list=categories_list)
                logging.info(
                    f"[ТехноМаркет] Добавлено {len(categories)} категорий в контекст."
                )
            else:
                self.context = base_context.format(
                    categories_list="категории не найдены"
                )
                logging.warning("[ТехноМаркет] Категории не найдены в БД.")
        except Exception as e:
            self.context = base_context.format(
                categories_list="ошибка загрузки категорий"
            )
            logging.error(f"[ТехноМаркет] Ошибка загрузки категорий: {e}")

    def save_context(self, new_context: str):
        self.context = new_context
        with CONTEXT_FILE.open("w", encoding="utf-8") as f:
            f.write(new_context)

    def reset_context(self):
        self.save_context(DEFAULT_CONTEXT)

    def reload_context_with_categories(self):
        """Перезагружает контекст с актуальными категориями из БД."""
        self.load_context()
        logging.info("[ТехноМаркет] Контекст перезагружен с актуальными категориями.")

    def get_context(self):
        return self.context

    def get_context_with_addition(self, additional_text: str) -> str:
        """Формирует контекст на основе self.context и дополняет его текстом из аргумента."""
        return f"{self.context}\n\n{additional_text}"


context_manager = ContextManager()

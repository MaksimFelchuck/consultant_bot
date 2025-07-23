import json
import logging
import os
from pathlib import Path

from config import DEFAULT_CONTEXT

CONTEXT_FILE = Path(__file__).parent / "context.txt"


class ContextManager:
    def __init__(self):
        self.context = DEFAULT_CONTEXT
        self.load_context()

    def load_context(self):
        if CONTEXT_FILE.exists():
            with CONTEXT_FILE.open("r", encoding="utf-8") as f:
                self.context = f.read()
            logging.info(
                f"[ТехноМаркет] Изначальный контекст для бота загружен из context.txt."
            )
        else:
            logging.info(
                f"[ТехноМаркет] Файл context.txt не найден, используется контекст по умолчанию."
            )

    def save_context(self, new_context: str):
        self.context = new_context
        with CONTEXT_FILE.open("w", encoding="utf-8") as f:
            f.write(new_context)

    def reset_context(self):
        self.save_context(DEFAULT_CONTEXT)

    def get_context(self):
        return self.context


context_manager = ContextManager()

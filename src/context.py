import json
import os
import logging
from pathlib import Path
from config import DEFAULT_CONTEXT

CONTEXT_FILE = Path(__file__).parent / 'context.txt'

class ContextManager:
    def __init__(self):
        self.context = DEFAULT_CONTEXT
        self.load_context()

    def load_context(self):
        if CONTEXT_FILE.exists():
            with CONTEXT_FILE.open('r', encoding='utf-8') as f:
                self.context = f.read()
            logging.info(f"[ТехноМаркет] Изначальный контекст для бота загружен из context.txt.")
        else:
            logging.info(f"[ТехноМаркет] Файл context.txt не найден, используется контекст по умолчанию.")

    def save_context(self, new_context: str):
        self.context = new_context
        with CONTEXT_FILE.open('w', encoding='utf-8') as f:
            f.write(new_context)

    def reset_context(self):
        self.save_context(DEFAULT_CONTEXT)

    def get_context(self):
        return self.context

def format_products_for_context(products_by_category: dict) -> str:
    """
    Формирует текст для ассистента с ассортиментом: по категориям, кратко.
    products_by_category: {category_name: [Product, ...], ...}
    """
    lines = ["Актуальный ассортимент ТехноМаркет:"]
    for cat, products in products_by_category.items():
        lines.append(f"\nКатегория: {cat}")
        for p in products:
            lines.append(f"- {p.name} — {p.price}₽. {p.description[:60]}...")
    return "\n".join(lines)

context_manager = ContextManager() 
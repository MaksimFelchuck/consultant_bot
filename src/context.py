import json
import os
import logging
from pathlib import Path
from config import DEFAULT_CONTEXT
from typing import Dict

CONTEXT_FILE = Path(__file__).parent / "context.txt"
ASSORTMENT_HEADER = "Актуальный ассортимент ТехноМаркет:"

class ContextManager:
    """Менеджер для работы с контекстом ассистента."""
    def __init__(self) -> None:
        self.context: str = DEFAULT_CONTEXT
        self.load_context()

    def load_context(self) -> None:
        if CONTEXT_FILE.exists():
            with CONTEXT_FILE.open("r", encoding="utf-8") as f:
                self.context = f.read()
            logging.info("[ТехноМаркет] Изначальный контекст для бота загружен из context.txt.")
        else:
            logging.info("[ТехноМаркет] Файл context.txt не найден, используется контекст по умолчанию.")

    def save_context(self, new_context: str) -> None:
        self.context = new_context
        with CONTEXT_FILE.open("w", encoding="utf-8") as f:
            f.write(new_context)

    def reset_context(self) -> None:
        self.save_context(DEFAULT_CONTEXT)

    def get_context(self) -> str:
        return self.context

def format_products_for_context(products_by_category: Dict[str, list]) -> str:
    """Формирует текст ассортимента по категориям для ассистента."""
    lines = [ASSORTMENT_HEADER]
    for cat, products in products_by_category.items():
        lines.append(f"\nКатегория: {cat}")
        for p in products:
            lines.append(f"- {p.name} — {p.price}₽. {p.description[:60]}...")
    return "\n".join(lines)

context_manager = ContextManager() 
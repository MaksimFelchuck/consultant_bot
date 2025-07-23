#!/usr/bin/env python3
"""
Скрипт для форматирования кода проекта.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Запускает команду и выводит результат."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} завершено успешно")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} завершено с ошибками:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка при {description}: {e}")
        return False


def main():
    """Основная функция форматирования."""
    print("🎨 Запуск форматирования кода...")

    # Проверяем, что мы в корне проекта
    if not Path("src").exists():
        print("❌ Ошибка: запустите скрипт из корня проекта")
        sys.exit(1)

    success = True

    # Форматируем код
    success &= run_command("black src/", "Форматирование кода (black)")
    success &= run_command(
        "isort src/ --skip=src/database/alembic/versions/",
        "Сортировка импортов (isort)",
    )

    # Проверяем код
    success &= run_command(
        "flake8 src/ --max-line-length=88 --ignore=E203,W503,E402,E501,F401,F402,F541,F841 --exclude=src/database/alembic/versions/",
        "Проверка стиля (flake8)",
    )
    # success &= run_command("mypy src/ --ignore-missing-imports", "Проверка типов (mypy)")

    if success:
        print("\n🎉 Все проверки пройдены успешно!")
    else:
        print("\n⚠️ Некоторые проверки не пройдены. Исправьте ошибки.")
        sys.exit(1)


if __name__ == "__main__":
    main()

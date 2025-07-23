# Форматирование кода

## Настройка IDE

### VS Code

1. Установите расширения из `.vscode/extensions.json`
2. Настройки уже сконфигурированы в `.vscode/settings.json`

**Автоматическое форматирование:**
- При сохранении файла код автоматически форматируется
- Импорты автоматически сортируются
- Включена проверка типов

### PyCharm

1. Установите форматтеры: `pip install black isort flake8`
2. Настройте External Tools:
   - **Black**: `black $FilePath$`
   - **isort**: `isort $FilePath$`
3. Включите "Format on Save"

## Команды форматирования

### Быстрое форматирование всего проекта
```bash
python format_code.py
```

### Отдельные команды

**Форматирование кода (Black):**
```bash
black src/
```

**Сортировка импортов (isort):**
```bash
isort src/ --skip=src/database/alembic/versions/
```

**Проверка стиля (flake8):**
```bash
flake8 src/ --max-line-length=88 --ignore=E203,W503,E402,E501,F401,F402,F541,F841
```

**Проверка типов (mypy):**
```bash
mypy src/ --ignore-missing-imports
```

## Конфигурация

### pyproject.toml
Содержит настройки для всех инструментов:
- **Black**: длина строки 88 символов
- **isort**: профиль black, известные пакеты
- **flake8**: игнорируемые ошибки
- **mypy**: настройки типизации

### .pre-commit-config.yaml
Git hooks для автоматической проверки при коммитах.

### Исключения
- **Миграции Alembic** (`src/database/alembic/versions/`) не сортируются, чтобы сохранить порядок импортов

## Игнорируемые ошибки

- **E203**: whitespace before ':'
- **W503**: line break before binary operator  
- **E402**: module level import not at top of file
- **E501**: line too long
- **F401**: imported but unused
- **F402**: import shadowed by loop variable
- **F541**: f-string is missing placeholders
- **F841**: local variable is assigned to but never used

## Рекомендации

1. **Всегда форматируйте код перед коммитом**
2. **Используйте автоматическое форматирование в IDE**
3. **Проверяйте код командой `python format_code.py`**
4. **Установите pre-commit hooks для автоматической проверки** 
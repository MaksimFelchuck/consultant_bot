class ProductCharacteristics:
    """Класс для управления характеристиками товаров."""

    # Ключевые параметры для поиска товаров
    KEY_PARAMS = [
        "цена",
        "бюджет",
        "бренд",
        "цвет",
        "характеристики",
        "размер",
        "модель",
        "объём",
        "оперативная память",
        "экран",
        "тип",
    ]

    # Параметры, которые не считаются характеристиками для поиска
    NON_CHARACTERISTIC_PARAMS = [
        "категория",
    ]

    # Ключи для словарей
    CATEGORY_KEY = "категория"
    LAST_CATEGORY_KEY = "last_category"
    SEARCH_PARAMS_KEY = "search_params"

    # Сообщения для пользователя
    DEFAULT_CATEGORY_NAME = "товарами"
    CLARIFICATION_MESSAGE_TEMPLATE = (
        "Вижу, что вы интересуетесь категорией {category_name}. "
        "Для подбора товара мне нужна дополнительная информация:\n\n"
        "• Бюджет (например: до 50000 рублей)\n"
        "• Бренд (например: Samsung, Apple, Xiaomi)\n"
        "• Цвет (например: черный, белый)\n"
        "• Другие важные характеристики\n\n"
        "Или просто опишите, что именно вы ищете!"
    )

    # Ключи для фильтров
    COLOR_FILTER_KEY = "цвет"
    BRAND_FILTER_KEY = "бренд"
    PRICE_FILTER_KEY = "цена"
    BUDGET_FILTER_KEY = "бюджет"
    TYPE_FILTER_KEY = "тип"

    # Ключевые слова для обработки сообщений
    PHOTO_KEYWORDS = ["фото", "картинка", "photo", "picture", "покажи", "show"]
    SPECS_KEYWORDS = [
        "характеристики",
        "характеристика",
        "описание",
        "подробности",
        "детали",
        "specs",
        "specifications",
    ]
    PRICE_KEYWORDS = ["цена", "стоимость", "price", "cost", "сколько стоит"]
    ORDER_KEYWORDS = [
        "заказ",
        "купить",
        "приобрести",
        "оформить",
        "order",
        "buy",
        "purchase",
    ]
    BACK_KEYWORDS = [
        "назад",
        "список",
        "другие",
        "еще",
        "back",
        "list",
        "other",
        "more",
    ]

    def __init__(self, params):
        self.params = params
        self.characteristics_only = self._filter_characteristics()

    def _filter_characteristics(self):
        """Фильтрует параметры, исключая не-характеристики."""
        return {
            k: v
            for k, v in self.params.items()
            if k not in self.NON_CHARACTERISTIC_PARAMS
        }

    def has_characteristics(self, ignore_words):
        """Проверяет наличие характеристик для поиска товаров."""
        return any(
            k in self.characteristics_only
            and self.characteristics_only[k]
            and self.characteristics_only[k] not in ignore_words
            for k in self.KEY_PARAMS
        )

    def get_characteristics(self, ignore_words: list[str]) -> list[str]:
        """Возвращает список найденных характеристик."""
        return [
            k
            for k in self.KEY_PARAMS
            if k in self.characteristics_only
            and self.characteristics_only[k]
            and self.characteristics_only[k] not in ignore_words
        ]

    def get_category(self) -> str:
        """Возвращает категорию товара."""
        return self.params.get(self.CATEGORY_KEY, "")

    def get_characteristics_dict(self) -> dict[str, any]:
        """Возвращает словарь только с характеристиками."""
        return self.characteristics_only.copy()

    @classmethod
    def get_clarification_message(cls, category_name: str) -> str:
        """Возвращает сообщение для уточнения характеристик."""
        return cls.CLARIFICATION_MESSAGE_TEMPLATE.format(
            category_name=category_name or cls.DEFAULT_CATEGORY_NAME
        )

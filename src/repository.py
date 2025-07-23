"""
Repository паттерн для работы с базой данных.
Современный подход к абстракции доступа к данным.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from database import SessionLocal
from database.models import Category, Product, User, Message
from database.service import get_or_create_user, save_message, get_user_history


class BaseRepository:
    """Базовый класс для всех репозиториев."""
    
    def __init__(self):
        self._session: Optional[Session] = None
    
    @property
    def session(self) -> Session:
        """Получает сессию БД."""
        if self._session is None:
            self._session = SessionLocal()
        return self._session
    
    def close(self):
        """Закрывает сессию БД."""
        if self._session:
            self._session.close()
            self._session = None


class CategoryRepository(BaseRepository):
    """Репозиторий для работы с категориями."""
    
    def get_all(self) -> List[Category]:
        """Получает все категории."""
        return self.session.query(Category).all()
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """Получает категорию по названию."""
        return self.session.query(Category).filter(
            Category.name.ilike(f"%{name}%")
        ).first()
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Получает категорию по ID."""
        return self.session.query(Category).filter(Category.id == category_id).first()


class ProductRepository(BaseRepository):
    """Репозиторий для работы с продуктами."""
    
    def search_products(
        self,
        category_id: Optional[int] = None,
        filters: Optional[Dict[str, List]] = None,
        limit: int = 3
    ) -> List[Product]:
        """
        Поиск продуктов с фильтрами.
        
        Args:
            category_id: ID категории для фильтрации
            filters: Словарь с фильтрами {'color': [...], 'brand': [...], 'spec': [...], 'price': [...]}
            limit: Максимальное количество результатов
        """
        query = self.session.query(Product)
        
        # Фильтр по категории
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # Применение фильтров
        if filters:
            if filters.get('color'):
                query = query.filter(or_(*filters['color']))
            if filters.get('brand'):
                query = query.filter(or_(*filters['brand']))
            if filters.get('spec'):
                query = query.filter(*filters['spec'])
            if filters.get('price'):
                query = query.filter(*filters['price'])
        
        return query.order_by(func.random()).limit(limit).all()
    
    def get_random_by_category(self, category_id: int, limit: int = 3) -> List[Product]:
        """Получает случайные продукты из категории."""
        return self.session.query(Product).filter(
            Product.category_id == category_id
        ).order_by(func.random()).limit(limit).all()
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Получает продукт по ID."""
        return self.session.query(Product).filter(Product.id == product_id).first()


class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями."""
    
    def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Получает или создает пользователя."""
        return get_or_create_user(
            self.session,
            telegram_id,
            username,
            first_name,
            last_name
        )
    
    def update_extra_data(self, user: User, extra_data: Dict[str, Any]):
        """Обновляет дополнительные данные пользователя."""
        user.extra_data = extra_data
        self.session.commit()
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получает пользователя по Telegram ID."""
        return self.session.query(User).filter(User.telegram_id == telegram_id).first()


class MessageRepository(BaseRepository):
    """Репозиторий для работы с сообщениями."""
    
    def save_message(self, user_id: int, role: str, content: str) -> Message:
        """Сохраняет сообщение."""
        return save_message(self.session, user_id, role, content)
    
    def get_user_history(self, user_id: int, limit: int = 5) -> List[Message]:
        """Получает историю сообщений пользователя."""
        return get_user_history(self.session, user_id, limit=limit)


class SearchService:
    """Сервис для поиска продуктов с умным ослаблением фильтров."""
    
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    def smart_search(
        self,
        category_id: Optional[int] = None,
        filters: Optional[Dict[str, List]] = None
    ) -> tuple[List[Product], List[str]]:
        """
        Умный поиск с поэтапным ослаблением фильтров.
        
        Returns:
            tuple: (список продуктов, список сброшенных фильтров)
        """
        if not filters:
            filters = {'color': [], 'brand': [], 'spec': [], 'price': []}
        
        # Попытка 1: все фильтры
        products = self.product_repo.search_products(category_id, filters, limit=3)
        if products:
            return products, []
        
        # Попытка 2: без цвета
        filters_without_color = {k: v for k, v in filters.items() if k != 'color'}
        products = self.product_repo.search_products(category_id, filters_without_color, limit=3)
        if products:
            return products, ['цвет']
        
        # Попытка 3: без цвета и бренда
        filters_without_brand = {k: v for k, v in filters_without_color.items() if k != 'brand'}
        products = self.product_repo.search_products(category_id, filters_without_brand, limit=3)
        if products:
            return products, ['цвет', 'бренд']
        
        # Попытка 4: только цена
        price_only = {'price': filters.get('price', [])}
        products = self.product_repo.search_products(category_id, price_only, limit=3)
        if products:
            return products, ['цвет', 'бренд', 'характеристики']
        
        # Попытка 5: случайные из категории
        if category_id:
            products = self.product_repo.get_random_by_category(category_id, limit=3)
            if products:
                return products, ['цвет', 'бренд', 'характеристики', 'цена']
        
        return [], ['цвет', 'бренд', 'характеристики', 'цена']


# Глобальные экземпляры репозиториев
category_repo = CategoryRepository()
product_repo = ProductRepository()
user_repo = UserRepository()
message_repo = MessageRepository()
search_service = SearchService(product_repo) 
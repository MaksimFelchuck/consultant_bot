"""add initial categories and products

Revision ID: ee48eb4ce95e
Revises: 6f3f1f10d8ab
Create Date: 2025-07-15 15:14:20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import datetime
import random
import json
import time

# revision identifiers, used by Alembic.
revision = 'ee48eb4ce95e'
down_revision = '6f3f1f10d8ab'
branch_labels = None
depends_on = None

def upgrade():
    # Маппинг категорий: кириллица -> латиница
    category_mapping = {
        "Смартфоны": "Smartphones",
        "Планшеты": "Tablets", 
        "Ноутбуки": "Laptops",
        "Телевизоры": "TVs",
        "Наушники": "Headphones",
        "Смарт-часы": "Smartwatches",
        "Фотоаппараты": "Cameras",
        "Игровые приставки": "Gaming_Consoles",
        "Мониторы": "Monitors",
        "Аксессуары": "Accessories",
    }
    
    categories = [
        ("Смартфоны", "smartphone"),
        ("Планшеты", "tablet"),
        ("Ноутбуки", "laptop"),
        ("Телевизоры", "tv"),
        ("Наушники", "headphones"),
        ("Смарт-часы", "smartwatch"),
        ("Фотоаппараты", "camera"),
        ("Игровые приставки", "console"),
        ("Мониторы", "monitor"),
        ("Аксессуары", "accessory"),
    ]
    conn = op.get_bind()
    now = datetime.datetime.utcnow()
    category_ids = []
    for name, _ in categories:
        res = conn.execute(
            sa.text("""
                INSERT INTO categories (name, created_at) VALUES (:name, :created_at) RETURNING id
            """),
            {"name": name, "created_at": now}
        )
        category_ids.append(res.scalar())

    # Примеры товаров для каждой категории (5 осмысленных + 95 рандомных)
    products_by_category = {
        "Смартфоны": [
            ("Apple iPhone 15 Pro", "Флагманский смартфон Apple с OLED-дисплеем, процессором A17 и тройной камерой.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
            ("Samsung Galaxy S24 Ultra", "Смартфон с большим Dynamic AMOLED 2X экраном, поддержкой S Pen и камерой 200 Мп.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Xiaomi 14 Pro", "Мощный смартфон с камерой Leica, Snapdragon 8 Gen 3 и быстрой зарядкой.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Google Pixel 8 Pro", "Чистый Android, топовая камера и уникальные AI-функции.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("OnePlus 12", "Флагман OnePlus с AMOLED-экраном 120 Гц и быстрой зарядкой.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Honor Magic6 Pro", "Смартфон с изогнутым дисплеем и камерой 180 Мп.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
            ("Nothing Phone (2)", "Уникальный дизайн, прозрачная задняя крышка и чистый Android.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Realme GT 5 Pro", "Быстрый смартфон с AMOLED-экраном и быстрой зарядкой 150 Вт.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Sony Xperia 1 V", "4K OLED-дисплей, профессиональная камера и защита IP68.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Asus Zenfone 10", "Компактный флагман с мощным процессором и стереозвуком.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
        ],
        "Планшеты": [
            ("Apple iPad Pro 12.9 (2024)", "Планшет для творчества и работы с поддержкой Apple Pencil 3-го поколения.", "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80"),
            ("Samsung Galaxy Tab S9 Ultra", "AMOLED-планшет с поддержкой S Pen и DeX-режимом.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Xiaomi Pad 6 Pro", "Доступный планшет с хорошей батареей и Snapdragon 8+ Gen 1.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Lenovo Tab Extreme", "Планшет с клавиатурой, стилусом и 3K-дисплеем.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Huawei MatePad Pro 13.2", "Планшет с HarmonyOS, OLED-экраном и поддержкой M-Pencil 3.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
        ],
        "Ноутбуки": [
            ("Apple MacBook Pro 16 (M3 Max)", "Профессиональный ноутбук на чипе M3 Max, Liquid Retina XDR дисплей.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("ASUS ROG Zephyrus G16", "Игровой ноутбук с RTX 4080 и Mini-LED дисплеем.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Dell XPS 13 Plus (2024)", "Компактный ультрабук с сенсорной панелью и OLED-экраном.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("HP Spectre x360 14", "Трансформер с сенсорным OLED-экраном и стилусом.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Lenovo ThinkPad X1 Carbon Gen 12", "Бизнес-ноутбук с легендарной клавиатурой и защитой.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Телевизоры": [
            ("LG OLED55C3", "4K OLED-телевизор с поддержкой Dolby Vision.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Samsung QN90C Neo QLED", "Яркий QLED-телевизор с тонкими рамками.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Sony XR-65A80L", "Телевизор с Google TV и отличным звуком.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("TCL 55C845", "Доступный QLED-телевизор с HDR.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Philips 50PUS8807", "Телевизор с Ambilight и Android TV.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Наушники": [
            ("Sony WH-1000XM5", "Беспроводные наушники с шумоподавлением.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Apple AirPods Pro 2", "TWS-наушники с активным шумоподавлением.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Sennheiser Momentum 4", "Аудиофильские наушники с отличным звуком.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("JBL Tune 760NC", "Доступные наушники с Bluetooth.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Xiaomi Redmi Buds 4 Pro", "Компактные TWS-наушники.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Смарт-часы": [
            ("Apple Watch Series 9", "Смарт-часы с датчиком температуры и ECG.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Samsung Galaxy Watch 6", "Часы с AMOLED-экраном и GPS.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Huawei Watch GT 4", "Долгая автономность и спортивные функции.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Amazfit GTR 4", "Универсальные смарт-часы с GPS.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Garmin Venu 3", "Премиальные часы для спорта и здоровья.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Фотоаппараты": [
            ("Canon EOS R8", "Беззеркальная камера для фото и видео.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Sony Alpha 7 IV", "Полнокадровая камера для профессионалов.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Nikon Z6 II", "Универсальная камера для путешествий.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Fujifilm X-T5", "Камера с ретро-дизайном и отличной цветопередачей.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Panasonic Lumix S5 II", "Компактная полнокадровая камера.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Игровые приставки": [
            ("Sony PlayStation 5", "Консоль нового поколения с SSD.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Microsoft Xbox Series X", "Мощная игровая приставка с Game Pass.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Nintendo Switch OLED", "Гибридная консоль для дома и поездок.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Valve Steam Deck", "Портативная игровая консоль для ПК-игр.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Sony PlayStation 4 Slim", "Классика для любителей эксклюзивов.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Мониторы": [
            ("LG UltraGear 27GN950", "4K игровой монитор с высокой герцовкой.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Samsung Odyssey G7", "Изогнутый монитор для геймеров.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Dell UltraSharp U2723QE", "Профессиональный монитор с USB-C.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("AOC 24G2U", "Доступный монитор с IPS-матрицей.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Philips 346B1C", "Широкоформатный монитор для работы и игр.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
        "Аксессуары": [
            ("Logitech MX Master 3S", "Премиальная беспроводная мышь.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"),
            ("Razer BlackWidow V4", "Механическая клавиатура для геймеров.", "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80"),
            ("Xiaomi Mi Power Bank 3", "Внешний аккумулятор на 20000 мАч.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80"),
            ("Samsung T7 Shield", "Портативный SSD для хранения данных.", "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80"),
            ("Apple AirTag", "Bluetooth-метка для поиска вещей.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80"),
        ],
    }

    # Списки брендов и моделей для генерации осмысленных имён
    smartphone_brands = [
        ("Apple", ["iPhone 13", "iPhone 14", "iPhone 15 Pro", "iPhone SE"]),
        ("Samsung", ["Galaxy S24", "Galaxy S23 FE", "Galaxy A54", "Galaxy M34"]),
        ("Xiaomi", ["Redmi Note 13 Pro", "Redmi 13C", "14 Pro", "Poco X6 Pro"]),
        ("Realme", ["12 Pro+", "C67", "GT 5 Pro"]),
        ("Honor", ["X8b", "90 Lite", "Magic6 Pro"]),
        ("Nothing", ["Phone (2)", "Phone (2a)"])
    ]
    smartphone_colors = ["Чёрный", "Белый", "Синий", "Зелёный", "Серый", "Красный"]
    smartphone_storage = ["64GB", "128GB", "256GB", "512GB"]

    # Аналогично для других категорий (пример для планшетов)
    tablet_brands = [
        ("Apple", ["iPad 10.2", "iPad Air 5", "iPad Pro 12.9"]),
        ("Samsung", ["Galaxy Tab S9", "Galaxy Tab A9", "Galaxy Tab S6 Lite"]),
        ("Xiaomi", ["Pad 6", "Pad 5"]),
        ("Lenovo", ["Tab M10", "Tab P12"]),
        ("Huawei", ["MatePad 11", "MatePad Pro"])
    ]
    tablet_colors = ["Серебристый", "Серый", "Чёрный", "Голубой"]
    tablet_storage = ["64GB", "128GB", "256GB"]

    # --- Ноутбуки ---
    laptop_brands = [
        ("Apple", ["MacBook Air M2", "MacBook Pro 16 M3"]),
        ("ASUS", ["VivoBook 15", "ROG Zephyrus G16", "ZenBook 14"]),
        ("Lenovo", ["ThinkPad X1 Carbon", "IdeaPad 3", "Yoga Slim 7"]),
        ("HP", ["Pavilion 14", "Spectre x360 14"]),
        ("Acer", ["Aspire 5", "Swift 3"]),
        ("MSI", ["Modern 15", "GF63 Thin"]),
        ("Huawei", ["MateBook D16", "MateBook X Pro"])
    ]
    laptop_colors = ["Серый", "Чёрный", "Серебристый", "Синий"]
    laptop_storage = ["512GB SSD", "1TB SSD", "256GB SSD"]

    # --- Наушники ---
    headphones_brands = [
        ("Sony", ["WH-1000XM5", "WF-C700N"]),
        ("Apple", ["AirPods Pro 2", "AirPods 3"]),
        ("JBL", ["Tune 510BT", "Live 660NC"]),
        ("Sennheiser", ["Momentum 4", "HD 450BT"]),
        ("Xiaomi", ["Redmi Buds 4 Pro", "Buds 3"]),
        ("Marshall", ["Major IV", "Motif II"])
    ]
    headphones_colors = ["Чёрный", "Белый", "Синий", "Бежевый"]

    # --- Телевизоры ---
    tv_brands = [
        ("LG", ["OLED55C3", "NanoCell 50NANO77"]),
        ("Samsung", ["Crystal UHD 55AU7100", "QN90C Neo QLED"]),
        ("Sony", ["XR-65A80L", "Bravia KD-55X85K"]),
        ("Philips", ["50PUS8807", "43PUS8508"]),
        ("TCL", ["55C845", "43P635"]),
        ("Xiaomi", ["TV A Pro 50", "TV Q2 55"]),
        ("Hisense", ["43A6K", "55U7KQ"])
    ]
    tv_sizes = ["43''", "50''", "55''", "65''"]

    # --- Смарт-часы ---
    watch_brands = [
        ("Apple", ["Watch Series 9", "Watch SE 2023"]),
        ("Samsung", ["Galaxy Watch 6", "Galaxy Watch 4"]),
        ("Huawei", ["Watch GT 4", "Watch Fit 3"]),
        ("Amazfit", ["Bip 5", "GTR 4"]),
        ("Garmin", ["Venu 3", "Forerunner 255"])
    ]
    watch_colors = ["Чёрный", "Белый", "Серебристый", "Розовый"]

    # --- Фотоаппараты ---
    camera_brands = [
        ("Canon", ["EOS 250D Kit", "EOS R8"]),
        ("Sony", ["Alpha 7 IV", "Alpha 6400"]),
        ("Nikon", ["Z6 II", "D5600"]),
        ("Fujifilm", ["X-T30 II", "X-T5"]),
        ("Panasonic", ["Lumix S5 II", "Lumix G100"])
    ]
    camera_types = ["Body", "Kit 18-55", "Kit 16-50"]

    # --- Игровые приставки ---
    console_brands = [
        ("Sony", ["PlayStation 5 Slim", "PlayStation 4 Pro"]),
        ("Microsoft", ["Xbox Series X", "Xbox Series S"]),
        ("Nintendo", ["Switch OLED", "Switch Lite"]),
        ("Valve", ["Steam Deck OLED"])
    ]
    console_colors = ["Чёрный", "Белый", "Красный"]

    # --- Мониторы ---
    monitor_brands = [
        ("LG", ["UltraGear 27GN950", "UltraWide 29WN600"]),
        ("Samsung", ["Odyssey G7", "Odyssey G5"]),
        ("Dell", ["UltraSharp U2723QE", "S2721HN"]),
        ("AOC", ["24G2U", "27G2SPAE"]),
        ("Philips", ["346B1C", "241E1S"]),
        ("BenQ", ["GW2480", "EX2710Q"])
    ]
    monitor_sizes = ["24''", "27''", "29''", "32''"]

    # --- Аксессуары ---
    accessory_brands = [
        ("Logitech", ["MX Master 3S", "M185"]),
        ("Razer", ["BlackWidow V4", "DeathAdder V2"]),
        ("Xiaomi", ["Mi Power Bank 3 10000mAh", "Mi Band 8"]),
        ("Kingston", ["DataTraveler 128GB", "A400 SSD 480GB"]),
        ("Baseus", ["GaN Charger 65W", "USB-C Hub"]),
        ("Apple", ["AirTag", "MagSafe Charger"])
    ]
    accessory_types = ["мышь", "клавиатура", "пауэрбанк", "флешка", "SSD", "зарядка", "метка", "хаб"]

    # Прямые ссылки на изображения для рандомных товаров (примерный пул)
    image_urls_pool = [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1519985176271-adb1088fa94c?auto=format&fit=crop&w=400&q=80"
    ]

    for cat_idx, (cat_name, cat_key) in enumerate(categories):
        cat_id = conn.execute(sa.text("SELECT id FROM categories WHERE name=:name"), {"name": cat_name}).scalar()
        # Генерируем 100 осмысленных товаров для каждой категории
        for i in range(1, 101):
            if cat_name == "Смартфоны":
                brand, models = random.choice(smartphone_brands)
                model = random.choice(models)
                color = random.choice(smartphone_colors)
                storage = random.choice(smartphone_storage)
                name = f"{brand} {model} {storage} ({color})"
                description = f"Смартфон {brand} {model} с {storage} памяти, цвет: {color}. Отличная камера, быстрый процессор, современный дизайн."
                specs = {"Экран": random.choice(["6.1" , "6.5", "6.7"]) + '" OLED', "Камера": f"{random.randint(12, 200)} Мп", "Батарея": f"{random.randint(3000, 6000)} мАч"}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Планшеты":
                brand, models = random.choice(tablet_brands)
                model = random.choice(models)
                color = random.choice(tablet_colors)
                storage = random.choice(tablet_storage)
                name = f"{brand} {model} {storage} ({color})"
                description = f"Планшет {brand} {model} с {storage} памяти, цвет: {color}. Подходит для работы, учёбы и развлечений."
                specs = {"Экран": random.choice(["10.2", "11", "12.9"]) + '" IPS', "Процессор": random.choice(["Apple M2", "Snapdragon 8+ Gen 1", "Kirin 9000"]), "Батарея": f"{random.randint(6000, 12000)} мАч"}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Ноутбуки":
                brand, models = random.choice(laptop_brands)
                model = random.choice(models)
                color = random.choice(laptop_colors)
                storage = random.choice(laptop_storage)
                name = f"{brand} {model} {storage} ({color})"
                description = f"Ноутбук {brand} {model} с {storage}, цвет: {color}. Для работы, учёбы и игр."
                specs = {"Экран": random.choice(["14", "15.6", "16"]) + '" IPS', "Процессор": random.choice(["Intel i7", "AMD Ryzen 7", "Apple M3"]), "ОЗУ": f"{random.choice([8, 16, 32])} ГБ"}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Телевизоры":
                brand, models = random.choice(tv_brands)
                model = random.choice(models)
                size = random.choice(tv_sizes)
                name = f"{brand} {model} {size}"
                description = f"Телевизор {brand} {model} диагональю {size}. Яркое изображение, умные функции."
                specs = {"Разрешение": random.choice(["4K", "8K", "FullHD"]), "Тип": random.choice(["OLED", "QLED", "LED"]), "Год": random.choice([2022, 2023, 2024])}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Наушники":
                brand, models = random.choice(headphones_brands)
                model = random.choice(models)
                color = random.choice(headphones_colors)
                name = f"{brand} {model} ({color})"
                description = f"Наушники {brand} {model}, цвет: {color}. Отличный звук и комфорт."
                specs = {"Тип": random.choice(["TWS", "Накладные", "Вкладыши"]), "Шумоподавление": random.choice(["Да", "Нет"]), "Время работы": f"{random.randint(5, 40)} ч"}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Смарт-часы":
                brand, models = random.choice(watch_brands)
                model = random.choice(models)
                color = random.choice(watch_colors)
                name = f"{brand} {model} ({color})"
                description = f"Смарт-часы {brand} {model}, цвет: {color}. Фитнес, уведомления, стиль."
                specs = {"Экран": random.choice(["AMOLED", "IPS"]), "GPS": random.choice(["Да", "Нет"]), "Влагозащита": random.choice(["IP68", "5ATM"])}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Фотоаппараты":
                brand, models = random.choice(camera_brands)
                model = random.choice(models)
                ctype = random.choice(camera_types)
                name = f"{brand} {model} {ctype}"
                description = f"Фотоаппарат {brand} {model} комплект: {ctype}. Для фото и видео."
                specs = {"Матрица": random.choice(["APS-C", "FullFrame", "Micro 4/3"]), "Мп": random.randint(16, 60), "Видео": random.choice(["4K", "8K", "FullHD"])}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Игровые приставки":
                brand, models = random.choice(console_brands)
                model = random.choice(models)
                color = random.choice(console_colors)
                name = f"{brand} {model} ({color})"
                description = f"Игровая приставка {brand} {model}, цвет: {color}. Современные игры и развлечения."
                specs = {"Поколение": random.choice(["9-е", "8-е"]), "Диск": random.choice(["SSD", "HDD"]), "Год": random.choice([2020, 2021, 2022, 2023])}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Мониторы":
                brand, models = random.choice(monitor_brands)
                model = random.choice(models)
                size = random.choice(monitor_sizes)
                name = f"{brand} {model} {size}"
                description = f"Монитор {brand} {model} диагональю {size}. Отличная цветопередача и частота обновления."
                specs = {"Разрешение": random.choice(["4K", "QHD", "FullHD"]), "Тип": random.choice(["IPS", "VA", "OLED"]), "Гц": random.choice([60, 75, 120, 144, 165])}
                image_url = random.choice(image_urls_pool)
            elif cat_name == "Аксессуары":
                brand, models = random.choice(accessory_brands)
                model = random.choice(models)
                atype = random.choice(accessory_types)
                name = f"{brand} {model} — {atype}"
                description = f"{atype.capitalize()} {brand} {model}. Полезный аксессуар для техники."
                specs = {"Тип": atype, "Совместимость": random.choice(["универсальный", "Apple", "Android"])}
                image_url = random.choice(image_urls_pool)
            else:
                name = f"{cat_name} {i}"
                description = f"Описание для {name} — современный товар категории {cat_name}."
                specs = {"spec1": f"value{random.randint(1, 10)}", "spec2": f"value{random.randint(1, 10)}"}
                image_url = random.choice(image_urls_pool)
            price = random.randint(1000, 150000)
            conn.execute(
                sa.text("""
                    INSERT INTO products (name, category_id, description, price, image_url, specs, created_at)
                    VALUES (:name, :category_id, :description, :price, :image_url, :specs, :created_at)
                """),
                {
                    "name": name,
                    "category_id": cat_id,
                    "description": description,
                    "price": price,
                    "image_url": image_url,
                    "specs": json.dumps(specs),
                    "created_at": now
                }
            )

def downgrade():
    op.execute("DELETE FROM products")
    op.execute("DELETE FROM categories")

-- Категории
INSERT INTO categories (name, created_at) VALUES
  ('Смартфоны', NOW()),
  ('Планшеты', NOW()),
  ('Ноутбуки', NOW()),
  ('Телевизоры', NOW()),
  ('Наушники', NOW()),
  ('Смарт-часы', NOW()),
  ('Фотоаппараты', NOW()),
  ('Игровые приставки', NOW()),
  ('Мониторы', NOW()),
  ('Аксессуары', NOW())
ON CONFLICT (name) DO NOTHING;

-- Смартфоны
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Apple iPhone 15 Pro', c.id, 'Флагман Apple с OLED-дисплеем, A17 Pro, камерой 48 Мп.', 139990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Apple iPhone 15 Pro' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Samsung Galaxy S24 Ultra', c.id, '6.8" AMOLED, Snapdragon 8 Gen 3, камера 200 Мп, S Pen.', 124990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Samsung Galaxy S24 Ultra' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Xiaomi 14 Pro', c.id, 'Snapdragon 8 Gen 3, камера Leica, 120 Вт зарядка.', 89990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Xiaomi 14 Pro' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Google Pixel 8 Pro', c.id, 'Чистый Android, топовая камера, OLED 120 Гц.', 109990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Google Pixel 8 Pro' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'OnePlus 12', c.id, 'AMOLED 120 Гц, Snapdragon 8 Gen 3, 100 Вт зарядка.', 79990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'OnePlus 12' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Honor Magic6 Pro', c.id, 'Изогнутый дисплей, камера 180 Мп, быстрая зарядка.', 74990, 'https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Honor Magic6 Pro' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sony Xperia 1 V', c.id, '4K OLED, камера Zeiss, защита IP68.', 99990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смартфоны'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sony Xperia 1 V' AND p.category_id = c.id);

-- Планшеты
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Apple iPad Pro 12.9 (2024)', c.id, 'Liquid Retina XDR, M4, поддержка Pencil Pro.', 129990, 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Планшеты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Apple iPad Pro 12.9 (2024)' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Samsung Galaxy Tab S9 Ultra', c.id, '14.6" AMOLED, S Pen, Snapdragon 8 Gen 2.', 99990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Планшеты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Samsung Galaxy Tab S9 Ultra' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Xiaomi Pad 6 Pro', c.id, 'Snapdragon 8+, 11" дисплей, 8600 мАч.', 49990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Планшеты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Xiaomi Pad 6 Pro' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Lenovo Tab Extreme', c.id, '3K OLED, клавиатура, стилус, 120 Гц.', 69990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Планшеты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Lenovo Tab Extreme' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Huawei MatePad Pro 13.2', c.id, 'HarmonyOS, OLED, M-Pencil 3.', 59990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Планшеты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Huawei MatePad Pro 13.2' AND p.category_id = c.id);

-- Ноутбуки
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Apple MacBook Pro 16 (M3 Max)', c.id, '16" Liquid Retina XDR, M3 Max, 36 ГБ RAM.', 299990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Ноутбуки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Apple MacBook Pro 16 (M3 Max)' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'ASUS ROG Zephyrus G16', c.id, 'RTX 4080, Mini-LED, Intel Core i9.', 189990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Ноутбуки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'ASUS ROG Zephyrus G16' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Dell XPS 13 Plus (2024)', c.id, '13.4" OLED, Intel Core Ultra 7, 32 ГБ RAM.', 159990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Ноутбуки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Dell XPS 13 Plus (2024)' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'HP Spectre x360 14', c.id, 'OLED, Intel Evo, стилус, 2-в-1.', 129990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Ноутбуки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'HP Spectre x360 14' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Lenovo ThinkPad X1 Carbon Gen 12', c.id, 'Бизнес-ноутбук, 14" IPS, Intel Core i7.', 119990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Ноутбуки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Lenovo ThinkPad X1 Carbon Gen 12' AND p.category_id = c.id);

-- Телевизоры
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'LG OLED55C3', c.id, '4K OLED, Dolby Vision, webOS.', 119990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Телевизоры'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'LG OLED55C3' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Samsung QN90C Neo QLED', c.id, '4K QLED, Quantum HDR 32x, Tizen.', 99990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Телевизоры'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Samsung QN90C Neo QLED' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sony XR-65A80L', c.id, '65" OLED, Google TV, Dolby Atmos.', 149990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Телевизоры'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sony XR-65A80L' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'TCL 55C845', c.id, 'QLED, 144 Гц, Google TV, HDR10+', 79990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Телевизоры'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'TCL 55C845' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Philips 50PUS8807', c.id, 'Ambilight, 4K, Android TV.', 69990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Телевизоры'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Philips 50PUS8807' AND p.category_id = c.id);

-- Наушники
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sony WH-1000XM5', c.id, 'Bluetooth, шумоподавление, 30 ч работы.', 39990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Наушники'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sony WH-1000XM5' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Apple AirPods Pro 2', c.id, 'TWS, ANC, MagSafe, до 6 ч.', 24990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Наушники'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Apple AirPods Pro 2' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sennheiser Momentum 4', c.id, 'Аудиофильский звук, до 60 ч работы.', 34990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Наушники'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sennheiser Momentum 4' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'JBL Tune 760NC', c.id, 'Доступные Bluetooth-наушники с ANC.', 9990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Наушники'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'JBL Tune 760NC' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Xiaomi Redmi Buds 4 Pro', c.id, 'TWS, Bluetooth 5.3, до 36 ч.', 5990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Наушники'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Xiaomi Redmi Buds 4 Pro' AND p.category_id = c.id);

-- Смарт-часы
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Apple Watch Series 9', c.id, 'Always-On Retina, датчик температуры, ECG.', 49990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смарт-часы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Apple Watch Series 9' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Samsung Galaxy Watch 6', c.id, 'AMOLED, GPS, пульс, 40 мм.', 34990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смарт-часы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Samsung Galaxy Watch 6' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Huawei Watch GT 4', c.id, 'AMOLED, 14 дней работы, GPS.', 24990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смарт-часы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Huawei Watch GT 4' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Amazfit GTR 4', c.id, 'AMOLED, GPS, 475 мАч, 150+ режимов.', 19990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смарт-часы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Amazfit GTR 4' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Garmin Venu 3', c.id, 'AMOLED, GPS, SpO2, 14 дней.', 39990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Смарт-часы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Garmin Venu 3' AND p.category_id = c.id);

-- Фотоаппараты
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Canon EOS R8', c.id, '24 Мп, 4K 60p, автофокус Dual Pixel.', 129990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Фотоаппараты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Canon EOS R8' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sony Alpha 7 IV', c.id, '33 Мп, 4K 60p, стабилизация, Wi-Fi.', 199990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Фотоаппараты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sony Alpha 7 IV' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Nikon Z6 II', c.id, '24 Мп, 4K, 273 точки автофокуса.', 159990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Фотоаппараты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Nikon Z6 II' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Fujifilm X-T5', c.id, '40 Мп, 6.2K видео, ретро-дизайн.', 139990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Фотоаппараты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Fujifilm X-T5' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Panasonic Lumix S5 II', c.id, '24 Мп, 6K видео, стабилизация.', 119990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Фотоаппараты'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Panasonic Lumix S5 II' AND p.category_id = c.id);

-- Игровые приставки
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sony PlayStation 5', c.id, '825 ГБ SSD, 4K, DualSense, эксклюзивы.', 69990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Игровые приставки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sony PlayStation 5' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Microsoft Xbox Series X', c.id, '1 ТБ SSD, 4K, Game Pass, Dolby Vision.', 64990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Игровые приставки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Microsoft Xbox Series X' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Nintendo Switch OLED', c.id, 'Гибридная консоль, 7" OLED, эксклюзивы.', 39990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Игровые приставки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Nintendo Switch OLED' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Valve Steam Deck', c.id, 'Портативная консоль, SteamOS, 512 ГБ.', 59990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Игровые приставки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Valve Steam Deck' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Sony PlayStation 4 Slim', c.id, '500 ГБ HDD, эксклюзивы, HDR.', 29990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Игровые приставки'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Sony PlayStation 4 Slim' AND p.category_id = c.id);

-- Мониторы
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'LG UltraGear 27GN950', c.id, '27" 4K, 144 Гц, Nano IPS, G-Sync.', 79990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Мониторы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'LG UltraGear 27GN950' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Samsung Odyssey G7', c.id, '32" QHD, 240 Гц, изогнутый, HDR600.', 59990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Мониторы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Samsung Odyssey G7' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Dell UltraSharp U2723QE', c.id, '27" 4K, IPS Black, USB-C, KVM.', 69990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Мониторы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Dell UltraSharp U2723QE' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'AOC 24G2U', c.id, '24" IPS, 144 Гц, FreeSync, эргономика.', 19990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Мониторы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'AOC 24G2U' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Philips 346B1C', c.id, '34" UWQHD, USB-C док, KVM.', 39990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Мониторы'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Philips 346B1C' AND p.category_id = c.id);

-- Аксессуары
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Logitech MX Master 3S', c.id, 'Премиальная беспроводная мышь, 8000 DPI.', 12990, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Аксессуары'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Logitech MX Master 3S' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Razer BlackWidow V4', c.id, 'Механическая клавиатура, RGB, макросы.', 17990, 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Аксессуары'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Razer BlackWidow V4' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Xiaomi Mi Power Bank 3', c.id, 'Внешний аккумулятор 20000 мАч, быстрая зарядка.', 4990, 'https://images.unsplash.com/photo-1512499617640-c2f999098c01?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Аксессуары'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Xiaomi Mi Power Bank 3' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Samsung T7 Shield', c.id, 'Портативный SSD, USB 3.2 Gen2, 1 ТБ.', 9990, 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Аксессуары'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Samsung T7 Shield' AND p.category_id = c.id);
INSERT INTO products (name, category_id, description, price, image_url, created_at)
SELECT 'Apple AirTag', c.id, 'Bluetooth-метка для поиска вещей, UWB.', 3990, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80', NOW()
FROM categories c
WHERE c.name = 'Аксессуары'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Apple AirTag' AND p.category_id = c.id); 
import os
import requests
from pathlib import Path
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; TechnoMarketBot/1.0; +https://technomarket.ru)'
}

photos = {
    'smartphones': {
        'smartphone1.jpg': 'https://cdn.pixabay.com/photo/2014/12/27/15/40/smartphone-581964_1280.jpg',
        'smartphone2.jpg': 'https://cdn.pixabay.com/photo/2016/11/29/09/32/phone-1869510_1280.jpg',
    },
    'laptops': {
        'laptop1.jpg': 'https://cdn.pixabay.com/photo/2014/05/02/21/50/home-office-336377_1280.jpg',
        'laptop2.jpg': 'https://cdn.pixabay.com/photo/2015/01/21/14/14/apple-606761_1280.jpg',
    },
    'headphones': {
        'headphones1.jpg': 'https://cdn.pixabay.com/photo/2016/11/29/09/32/headphones-1868612_1280.jpg',
        'headphones2.jpg': 'https://cdn.pixabay.com/photo/2017/01/06/19/15/headphones-1954636_1280.jpg',
    },
    'tv': {
        'tv1.jpg': 'https://cdn.pixabay.com/photo/2014/09/07/21/52/tv-438449_1280.jpg',
        'tv2.jpg': 'https://cdn.pixabay.com/photo/2016/11/29/09/32/television-1868572_1280.jpg',
    },
    # ... добавьте остальные категории по аналогии ...
}

base_dir = Path(__file__).parent
images_dir = base_dir

for cat, files in photos.items():
    cat_dir = images_dir / cat
    cat_dir.mkdir(exist_ok=True)
    for fname, url in files.items():
        fpath = cat_dir / fname
        if fpath.exists():
            print(f"[SKIP] {fpath} уже существует")
            continue
        print(f"[DL] {url} -> {fpath}")
        try:
            resp = requests.get(url, timeout=20, headers=headers)
            resp.raise_for_status()
            with open(fpath, "wb") as f:
                f.write(resp.content)
            time.sleep(1)
        except Exception as e:
            print(f"[ERR] {url}: {e}") 
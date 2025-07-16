import os
import psycopg2

SQL_FILE = 'init_data.sql'
DATABASE_URL = os.getenv('DATABASE_URL') or 'postgresql://user:password@localhost:5432/consultant_bot'

def run_sql_file(sql_file, conn):
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute('BEGIN;')
        for statement in sql.split(';'):
            stmt = statement.strip()
            if stmt:
                cur.execute(stmt)
        cur.execute('COMMIT;')
    print('Данные успешно загружены.')

def main():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        run_sql_file(SQL_FILE, conn)
    finally:
        conn.close()

if __name__ == '__main__':
    main() 
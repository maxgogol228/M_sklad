import sqlite3
import os

DB_PATH = 'db.sqlite3'

def setup_database():
    print("🚀 Начинаем настройку базы данных...")
    
    # Удаляем старый файл, если он есть, чтобы начать с чистого листа
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Старый файл базы данных удалён.")
    
    # Создаём подключение (автоматически создаст файл)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("➕ Создан новый файл базы данных.")

    # --- Создание всех таблиц ---
    print("📋 Создание таблиц...")
    
    cursor.execute("""
    CREATE TABLE stock_part (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) UNIQUE NOT NULL,
        sku VARCHAR(100) NOT NULL DEFAULT '',
        quantity REAL NOT NULL DEFAULT 0,
        critical_minimum REAL NOT NULL DEFAULT 0,
        delivery_days INTEGER NOT NULL DEFAULT 7,
        image VARCHAR(100),
        is_consumable BOOLEAN NOT NULL DEFAULT 0,
        consumable_per_device REAL NOT NULL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE stock_device (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        image VARCHAR(100),
        production_per_day INTEGER NOT NULL DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE stock_devicepart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        part_id INTEGER NOT NULL,
        quantity_per_device REAL NOT NULL DEFAULT 1,
        FOREIGN KEY (device_id) REFERENCES stock_device(id),
        FOREIGN KEY (part_id) REFERENCES stock_part(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE stock_order (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_id INTEGER NOT NULL,
        quantity_ordered REAL NOT NULL,
        order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_received BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (part_id) REFERENCES stock_part(id)
    )
    """)
    
    # (Опционально) Добавьте сюда ещё таблицы, если они у вас есть.
    # Например, для расходников, если они у вас отдельно.
    
    conn.commit()
    conn.close()
    print("✅ Все таблицы успешно созданы!")
    print("🎉 База данных готова к работе.")

if __name__ == "__main__":
    setup_database()

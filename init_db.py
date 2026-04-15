import sqlite3
import os

DB_PATH = 'db.sqlite3'

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица AccessKey
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_accesskey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(100) UNIQUE NOT NULL,
            level VARCHAR(20) NOT NULL DEFAULT 'observer',
            is_active BOOLEAN NOT NULL DEFAULT 0,
            created_by VARCHAR(100) NOT NULL DEFAULT '',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            activated_at TIMESTAMP NULL,
            user_name VARCHAR(100) NOT NULL DEFAULT ''
        )
    """)
    
    # Таблица UserSession
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_usersession (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name VARCHAR(100) NOT NULL,
            access_key_hash VARCHAR(128) NOT NULL,
            device_id VARCHAR(200) NOT NULL,
            last_login TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
    """)
    
    # Таблица Part
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_part (
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
    
    # Таблица Device
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_device (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            image VARCHAR(100),
            production_per_day INTEGER NOT NULL DEFAULT 1
        )
    """)
    
    # Таблица DevicePart
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_devicepart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            quantity_per_device REAL NOT NULL DEFAULT 1
        )
    """)
    
    # Таблица Order
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_order (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER NOT NULL,
            quantity_ordered REAL NOT NULL,
            order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_received BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Таблица Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user VARCHAR(100) NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45)
        )
    """)
    
    # Ключ администратора
    cursor.execute("SELECT COUNT(*) FROM stock_accesskey WHERE key = '//admpan1993//'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO stock_accesskey (key, level, is_active, created_by, user_name)
            VALUES ('//admpan1993//', 'admin', 1, 'system', 'Администратор')
        """)
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

if __name__ == '__main__':
    init_database()

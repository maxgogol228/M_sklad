from django.apps import AppConfig
import sqlite3
import os

class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock'

    def ready(self):
        """Создаёт все таблицы при запуске приложения, если их нет"""
        from django.conf import settings
        
        db_path = settings.DATABASES['default']['NAME']
        
        # Ждём немного, чтобы Django успел инициализироваться
        import time
        time.sleep(2)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Таблица stock_device
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_device (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                image VARCHAR(100),
                production_per_day INTEGER NOT NULL DEFAULT 1
            )
        """)
        
        # Таблица stock_part
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
        
        # Таблица stock_devicepart
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_devicepart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                quantity_per_device REAL NOT NULL DEFAULT 1
            )
        """)
        
        # Таблица stock_order
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_order (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                quantity_ordered REAL NOT NULL,
                order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_received BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Все таблицы созданы или уже существовали")

from django.apps import AppConfig
import sqlite3
import os

class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock'

    def ready(self):
        """Автоматически добавляет недостающие колонки в таблицы"""
        from django.conf import settings
        
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем наличие колонки order_link в таблице stock_part
        cursor.execute("PRAGMA table_info(stock_part)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'order_link' not in columns:
            cursor.execute("ALTER TABLE stock_part ADD COLUMN order_link VARCHAR(500)")
            print("✅ Добавлена колонка order_link в таблицу stock_part")
            conn.commit()
        
        conn.close()

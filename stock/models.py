from django.db import models
from django.contrib.auth.models import User
import bcrypt
from django.db import connection

class AccessKey(models.Model):
    LEVEL_CHOICES = [
        ('observer', 'Наблюдатель'),
        ('full', 'Полный доступ'),
        ('admin', 'Доступ к админ панели'),
    ]
    key = models.CharField(max_length=100, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='observer')
    is_active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    user_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.key} ({self.level})"

class UserSession(models.Model):
    user_name = models.CharField(max_length=100)
    access_key_hash = models.CharField(max_length=128)
    device_id = models.CharField(max_length=200)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class Part(models.Model):
    name = models.CharField(max_length=200, unique=True)
    sku = models.CharField(max_length=100, blank=True)
    quantity = models.FloatField(default=0)
    critical_minimum = models.FloatField(default=0)
    delivery_days = models.IntegerField(default=7)
    image = models.ImageField(upload_to='parts/', blank=True, null=True)
    is_consumable = models.BooleanField(default=False)
    consumable_per_device = models.FloatField(default=0, help_text="Для расходников: сколько на 1 прибор")

class Device(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='devices/', blank=True, null=True)
    production_per_day = models.IntegerField(default=1)

class DevicePart(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity_per_device = models.FloatField(default=1)

class Order(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity_ordered = models.FloatField()
    order_date = models.DateTimeField(auto_now_add=True)
    is_received = models.BooleanField(default=False)

class Log(models.Model):
    user = models.CharField(max_length=100)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)

# Функция для принудительного пересоздания таблицы
def force_recreate_table():
    """Полностью пересоздаёт таблицу stock_accesskey с правильной структурой"""
    with connection.cursor() as cursor:
        try:
            # Удаляем старую таблицу
            cursor.execute("DROP TABLE IF EXISTS stock_accesskey")
            print("✅ Старая таблица удалена")
            
            # Создаём новую таблицу
            cursor.execute("""
                CREATE TABLE stock_accesskey (
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
            print("✅ Новая таблица создана")
            
            # Создаём ключ администратора
            key = "//admpan1993//"
            key_hash = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()
            cursor.execute("""
                INSERT INTO stock_accesskey (key, level, is_active, created_by, user_name)
                VALUES (%s, 'admin', 1, 'system', 'Администратор')
            """, [key])
            print("✅ Ключ администратора создан: //admpan1993//")
            
        except Exception as e:
            print(f"Ошибка: {e}")

# Вызываем функцию при загрузке модуля
try:
    force_recreate_table()
except Exception as e:
    print(f"Table creation error: {e}")

from django.db import models
from django.contrib.auth.models import User
from django import template
from django.db import connection
register = template.Library()

class AccessKey(models.Model):
    LEVEL_CHOICES = [
        ('observer', 'Наблюдатель'),
        ('full', 'Полный доступ'),
        ('admin', 'Доступ к админ панели'),
    ]
    key = models.CharField(max_length=100, unique=True)  # Сам ключ (не хэш)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='observer')
    is_active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    user_name = models.CharField(max_length=100, blank=True)  # Имя пользователя при входе

class AdminPassword(models.Model):
    """Хранит пароль администратора"""
    password_hash = models.CharField(max_length=128)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_password(cls):
        obj = cls.objects.first()
        if not obj:
            # Создаём пароль по умолчанию
            import bcrypt
            default_hash = bcrypt.hashpw(b"//admpan1993//", bcrypt.gensalt()).decode()
            obj = cls.objects.create(password_hash=default_hash)
        return obj.password_hash

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




@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) if dictionary else 0


def force_update_table():
    """Создаёт или обновляет таблицу AccessKey при запуске"""
    with connection.cursor() as cursor:
        # Проверяем, есть ли колонка 'key'
        cursor.execute("PRAGMA table_info(stock_accesskey)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'key' not in columns and 'key_hash' in columns:
            # Переименовываем старую колонку
            cursor.execute("ALTER TABLE stock_accesskey RENAME COLUMN key_hash TO key")
        elif 'key' not in columns:
            # Добавляем новую колонку
            cursor.execute("ALTER TABLE stock_accesskey ADD COLUMN key VARCHAR(100) UNIQUE")
            
        # Добавляем остальные колонки, если их нет
        new_columns = ['level', 'is_active', 'created_by', 'created_at', 'activated_at', 'user_name']
        for col in new_columns:
            if col not in columns:
                cursor.execute(f"ALTER TABLE stock_accesskey ADD COLUMN {col} {'TEXT' if col != 'is_active' else 'BOOLEAN DEFAULT 0'}")

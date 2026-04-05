import os
import django
import bcrypt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msklad.settings')
django.setup()

from stock.models import AccessKey

key = "ADMIN-KEY-2024"
key_hash = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()

AccessKey.objects.create(
    key_hash=key_hash,
    level='full',
    is_active=True,
    comment='Первый администратор'
)

print(f"Ключ создан: {key}")

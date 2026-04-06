import bcrypt
from stock.models import AccessKey

key = "ADMIN-KEY-2024"
key_hash = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()

AccessKey.objects.create(
    key_hash=key_hash,
    level='full',
    is_active=True,
    comment='Администратор'
)

print("✅ Ключ создан:", key)
exit()

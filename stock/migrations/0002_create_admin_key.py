from django.db import migrations
import bcrypt

def create_admin_key(apps, schema_editor):
    AccessKey = apps.get_model('stock', 'AccessKey')
    
    # Проверяем, есть ли уже ключи
    if AccessKey.objects.exists():
        return
    
    # Создаём ключ администратора
    key = "1993parol1993"
    key_hash = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()
    
    AccessKey.objects.create(
        key_hash=key_hash,
        level='full',
        is_active=True,
        comment='Администратор'
    )

class Migration(migrations.Migration):
    dependencies = [
        ('stock', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_admin_key),
    ]

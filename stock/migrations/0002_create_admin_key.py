from django.db import migrations

def create_admin_key(apps, schema_editor):
    AccessKey = apps.get_model('stock', 'AccessKey')
    if not AccessKey.objects.filter(key='//admpan1993//').exists():
        AccessKey.objects.create(
            key='//admpan1993//',
            level='admin',
            is_active=True,
            created_by='system',
            user_name='Администратор'
        )

class Migration(migrations.Migration):
    dependencies = [
        ('stock', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_admin_key),
    ]

from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True)),
                ('level', models.CharField(choices=[('observer', 'Наблюдатель'), ('full', 'Полный доступ'), ('admin', 'Доступ к админ панели')], default='observer', max_length=20)),
                ('is_active', models.BooleanField(default=False)),
                ('created_by', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('activated_at', models.DateTimeField(blank=True, null=True)),
                ('user_name', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='devices/')),
                ('production_per_day', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100)),
                ('action', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('sku', models.CharField(blank=True, max_length=100)),
                ('quantity', models.FloatField(default=0)),
                ('critical_minimum', models.FloatField(default=0)),
                ('delivery_days', models.IntegerField(default=7)),
                ('image', models.ImageField(blank=True, null=True, upload_to='parts/')),
                ('is_consumable', models.BooleanField(default=False)),
                ('consumable_per_device', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=100)),
                ('access_key_hash', models.CharField(max_length=128)),
                ('device_id', models.CharField(max_length=200)),
                ('last_login', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='DevicePart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_per_device', models.FloatField(default=1)),
                ('device', models.ForeignKey(on_delete=models.CASCADE, to='stock.device')),
                ('part', models.ForeignKey(on_delete=models.CASCADE, to='stock.part')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_ordered', models.FloatField()),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('is_received', models.BooleanField(default=False)),
                ('part', models.ForeignKey(on_delete=models.CASCADE, to='stock.part')),
            ],
        ),
    ]

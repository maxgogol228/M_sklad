import json
import os
import bcrypt
import uuid
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.db import connection
from .models import *

def ensure_password_file():
    """Создаёт файл с паролем администратора, если его нет"""
    password_file = 'admin_password.txt'
    if not os.path.exists(password_file):
        with open(password_file, 'w') as f:
            f.write("//admpan1993//")
        print("✅ Создан файл admin_password.txt")

def ensure_admin_key():
    """Создаёт ключ администратора, если его нет"""
    from .models import AccessKey
    
    # Проверяем, есть ли активный ключ с уровнем admin
    if not AccessKey.objects.filter(is_active=True, level='admin').exists():
        # Создаём ключ администратора
        AccessKey.objects.create(
            key="//admpan1993//",
            level='admin',
            is_active=True,
            created_by='system',
            user_name='Администратор'
        )
        print("✅ Создан ключ администратора: //admpan1993//")

def login_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('name', '').strip()
        access_key = request.POST.get('key', '').strip()
        
        from .models import AccessKey
        
        try:
            key_obj = AccessKey.objects.get(key=access_key, is_active=True)
            request.session['user_name'] = user_name
            request.session['access_level'] = key_obj.level
            request.session['key_id'] = key_obj.id
            request.session['is_admin'] = (key_obj.level == 'admin')
            
            if key_obj.level == 'admin':
                return redirect('/admin-panel/')
            return redirect('/dashboard/')
            
        except AccessKey.DoesNotExist:
            # Первый вход с мастер-ключом
            if access_key == "//admpan1993//":
                key_obj, created = AccessKey.objects.get_or_create(
                    key="//admpan1993//",
                    defaults={
                        'level': 'admin',
                        'is_active': True,
                        'created_by': 'system',
                        'user_name': 'Администратор'
                    }
                )
                request.session['user_name'] = user_name
                request.session['access_level'] = 'admin'
                request.session['is_admin'] = True
                return redirect('/admin-panel/')
            
            messages.error(request, 'Неверный ключ доступа')
    
    return render(request, 'stock/login.html')

def get_admin_password_from_file():
    """Читает пароль из файла или возвращает значение по умолчанию"""
    password_file = 'admin_password.txt'
    if os.path.exists(password_file):
        with open(password_file, 'r') as f:
            return f.read().strip()
    return "//admpan1993//"

def update_admin_password(request):
    """Обновление пароля администратора (только для админов)"""
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            with open('admin_password.txt', 'w') as f:
                f.write(new_password)
            Log.objects.create(
                user=request.session.get('user_name', 'admin'),
                action='Сменил пароль администратора',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return JsonResponse({'success': True})
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)


def admin_panel_keys(request):
    """Управление ключами в админ-панели"""
    if not request.session.get('is_admin'):
        return redirect('/login/')
    
    keys = AccessKey.objects.all().order_by('-created_at')
    return render(request, 'stock/admin_keys.html', {'keys': keys})

def activate_key(request, key_id):
    """Активация ключа"""
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    key = get_object_or_404(AccessKey, id=key_id)
    key.is_active = True
    key.activated_at = now()
    key.save()
    
    Log.objects.create(
        user=request.session.get('user_name', 'admin'),
        action=f'Активировал ключ {key.key} с уровнем {key.level}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({'success': True})

def update_key_level(request, key_id):
    """Изменение уровня доступа ключа"""
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    key = get_object_or_404(AccessKey, id=key_id)
    new_level = request.POST.get('level')
    if new_level in dict(AccessKey.LEVEL_CHOICES):
        key.level = new_level
        key.save()
        
        Log.objects.create(
            user=request.session.get('user_name', 'admin'),
            action=f'Изменил уровень ключа {key.key} на {new_level}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Неверный уровень'}, status=400)

def delete_key(request, key_id):
    """Удаление ключа"""
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    key = get_object_or_404(AccessKey, id=key_id)
    key.delete()
    
    Log.objects.create(
        user=request.session.get('user_name', 'admin'),
        action=f'Удалил ключ {key.key}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({'success': True})


def create_test_key(request):
    key = "TEST-KEY-123"
    key_hash = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()
    AccessKey.objects.create(
        key_hash=key_hash,
        level='full',
        is_active=True,
        comment='Тестовый ключ'
    )
    return HttpResponse(f"Ключ создан: {key}")

@csrf_exempt
def run_migrations(request):
    if request.GET.get('secret') == 'YOUR_SECRET_KEY':
        call_command('migrate', interactive=False)
        return HttpResponse("Миграции выполнены")
    return HttpResponse("Нет доступа", status=403)

def check_access(request, required_level=None):
    """Проверка уровня доступа"""
    if not hasattr(request, 'access_level'):
        return False
    if required_level == 'full' and request.access_level != 'full':
        return False
    if required_level == 'readonly' and request.access_level == 'readonly':
        return False
    return True

def login_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('name')
        access_key = request.POST.get('key')
        device_id = request.POST.get('device_id') or str(uuid.uuid4())

        try:
            # Поиск ключа (хэширование введённого ключа и сравнение)
            all_keys = AccessKey.objects.filter(is_active=True)
            found_key = None
            for ak in all_keys:
                if bcrypt.checkpw(access_key.encode(), ak.key_hash.encode()):
                    found_key = ak
                    break
            
            if found_key:
                session, created = UserSession.objects.get_or_create(
                    device_id=device_id,
                    defaults={
                        'user_name': user_name,
                        'access_key_hash': found_key.key_hash
                    }
                )
                if not created:
                    session.user_name = user_name
                    session.access_key_hash = found_key.key_hash
                session.last_login = now()
                session.is_active = True
                session.save()
                
                response = redirect('/')
                response.set_cookie('device_id', device_id, max_age=604800)
                response.set_cookie('user_name', user_name, max_age=604800)
                messages.success(request, f'Добро пожаловать, {user_name}!')
                return response
            else:
                messages.error(request, 'Неверный ключ доступа')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
    
    return render(request, 'stock/login.html')

def logout_view(request):
    response = redirect('/login')
    response.delete_cookie('device_id')
    response.delete_cookie('user_name')
    messages.info(request, 'Вы вышли из системы')
    return response

def dashboard(request):
    if not check_access(request):
        return redirect('/login')
    
    # Детали
    parts = Part.objects.filter(is_consumable=False)
    for p in parts:
        # Расчёт суммарного потребления в день
        device_parts = DevicePart.objects.filter(part=p)
        total_per_day = 0
        for dp in device_parts:
            total_per_day += dp.quantity_per_device * dp.device.production_per_day
        p.daily_consumption = total_per_day
        p.days_left = int(p.quantity / total_per_day) if total_per_day > 0 else 999
        p.needs_order = p.quantity <= p.critical_minimum
    
    # Расходники
    consumables = Part.objects.filter(is_consumable=True)
    for c in consumables:
        c.devices_count = int(c.quantity / c.consumable_per_device) if c.consumable_per_device > 0 else 0
    
    # Критические позиции
    critical_parts = [p for p in parts if p.needs_order]
    
    context = {
        'parts': parts,
        'consumables': consumables,
        'critical_parts': critical_parts,
        'user_name': request.COOKIES.get('user_name', ''),
        'access_level': request.access_level if hasattr(request, 'access_level') else 'readonly'
    }
    return render(request, 'stock/dashboard.html', context)

def parts_list(request):
    if not check_access(request):
        return redirect('/login')
    
    parts = Part.objects.filter(is_consumable=False)
    
    # Фильтрация
    search = request.GET.get('search', '')
    if search:
        parts = parts.filter(name__icontains=search)
    
    # Расчёт дней
    for p in parts:
        device_parts = DevicePart.objects.filter(part=p)
        total_per_day = 0
        for dp in device_parts:
            total_per_day += dp.quantity_per_device * dp.device.production_per_day
        p.days_left = int(p.quantity / total_per_day) if total_per_day > 0 else 999
    
    paginator = Paginator(parts, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'parts': page_obj,
        'is_editable': request.access_level == 'full',
        'search': search
    }
    return render(request, 'stock/parts_list.html', context)

def part_add(request):
    if not check_access(request, 'full'):
        messages.error(request, 'Недостаточно прав')
        return redirect('/parts/')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        quantity = float(request.POST.get('quantity', 0))
        critical_minimum = float(request.POST.get('critical_minimum', 0))
        delivery_days = int(request.POST.get('delivery_days', 7))
        
        part = Part.objects.create(
            name=name,
            sku=sku,
            quantity=quantity,
            critical_minimum=critical_minimum,
            delivery_days=delivery_days,
            is_consumable=False
        )
        
        if request.FILES.get('image'):
            part.image = request.FILES['image']
            part.save()
        
        # Логирование
        Log.objects.create(
            user=request.COOKIES.get('user_name', 'unknown'),
            action=f'Добавил деталь: {name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Деталь "{name}" добавлена')
        return redirect('/parts/')
    
    return render(request, 'stock/part_form.html', {'title': 'Добавить деталь'})

def part_edit(request, part_id):
    if not check_access(request, 'full'):
        messages.error(request, 'Недостаточно прав')
        return redirect('/parts/')
    
    part = get_object_or_404(Part, id=part_id, is_consumable=False)
    
    if request.method == 'POST':
        part.name = request.POST.get('name')
        part.sku = request.POST.get('sku')
        part.quantity = float(request.POST.get('quantity', 0))
        part.critical_minimum = float(request.POST.get('critical_minimum', 0))
        part.delivery_days = int(request.POST.get('delivery_days', 7))
        
        if request.FILES.get('image'):
            if part.image:
                part.image.delete()
            part.image = request.FILES['image']
        
        part.save()
        
        Log.objects.create(
            user=request.COOKIES.get('user_name', 'unknown'),
            action=f'Редактировал деталь: {part.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Изменения сохранены')
        return redirect('/parts/')
    
    return render(request, 'stock/part_form.html', {'part': part, 'title': 'Редактировать деталь'})

def part_delete(request, part_id):
    if not check_access(request, 'full'):
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    part = get_object_or_404(Part, id=part_id)
    name = part.name
    part.delete()
    
    Log.objects.create(
        user=request.COOKIES.get('user_name', 'unknown'),
        action=f'Удалил деталь: {name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({'success': True})

def devices_list(request):
    if not check_access(request):
        return redirect('/login')
    
    devices = Device.objects.all()
    for d in devices:
        d.parts_count = DevicePart.objects.filter(device=d).count()
    
    context = {
        'devices': devices,
        'is_editable': request.access_level == 'full'
    }
    return render(request, 'stock/devices_list.html', context)

def device_add(request):
    if not check_access(request, 'full'):
        messages.error(request, 'Недостаточно прав')
        return redirect('/devices/')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        production_per_day = int(request.POST.get('production_per_day', 1))
        
        device = Device.objects.create(
            name=name,
            production_per_day=production_per_day
        )
        
        if request.FILES.get('image'):
            device.image = request.FILES['image']
            device.save()
        
        # Добавление деталей к прибору
        part_ids = request.POST.getlist('part_ids')
        quantities = request.POST.getlist('quantities')
        for part_id, qty in zip(part_ids, quantities):
            if part_id and qty:
                DevicePart.objects.create(
                    device=device,
                    part_id=int(part_id),
                    quantity_per_device=float(qty)
                )
        
        Log.objects.create(
            user=request.COOKIES.get('user_name', 'unknown'),
            action=f'Добавил прибор: {name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Прибор "{name}" добавлен')
        return redirect('/devices/')
    
    parts = Part.objects.filter(is_consumable=False)
    return render(request, 'stock/device_form.html', {'parts': parts, 'title': 'Добавить прибор'})

def device_edit(request, device_id):
    if not check_access(request, 'full'):
        messages.error(request, 'Недостаточно прав')
        return redirect('/devices/')
    
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        device.name = request.POST.get('name')
        device.production_per_day = int(request.POST.get('production_per_day', 1))
        
        if request.FILES.get('image'):
            if device.image:
                device.image.delete()
            device.image = request.FILES['image']
        
        device.save()
        
        # Обновление состава
        DevicePart.objects.filter(device=device).delete()
        part_ids = request.POST.getlist('part_ids')
        quantities = request.POST.getlist('quantities')
        for part_id, qty in zip(part_ids, quantities):
            if part_id and qty:
                DevicePart.objects.create(
                    device=device,
                    part_id=int(part_id),
                    quantity_per_device=float(qty)
                )
        
        Log.objects.create(
            user=request.COOKIES.get('user_name', 'unknown'),
            action=f'Редактировал прибор: {device.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Изменения сохранены')
        return redirect('/devices/')
    
    parts = Part.objects.filter(is_consumable=False)
    device_parts = {dp.part_id: dp.quantity_per_device for dp in DevicePart.objects.filter(device=device)}
    return render(request, 'stock/device_form.html', {
        'device': device,
        'parts': parts,
        'device_parts': device_parts,
        'title': 'Редактировать прибор'
    })

def consumables_list(request):
    if not check_access(request):
        return redirect('/login')
    
    consumables = Part.objects.filter(is_consumable=True)
    
    for c in consumables:
        c.devices_count = int(c.quantity / c.consumable_per_device) if c.consumable_per_device > 0 else 0
    
    context = {
        'consumables': consumables,
        'is_editable': request.access_level == 'full'
    }
    return render(request, 'stock/consumables_list.html', context)

def create_order(request, part_id):
    if not check_access(request):
        return redirect('/login')
    
    part = get_object_or_404(Part, id=part_id)
    
    if request.method == 'POST':
        quantity = float(request.POST.get('quantity', 0))
        
        order = Order.objects.create(
            part=part,
            quantity_ordered=quantity,
            is_received=False
        )
        
        Log.objects.create(
            user=request.COOKIES.get('user_name', 'unknown'),
            action=f'Создал заказ на {part.name}: {quantity} шт',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Заказ на {part.name} создан')
        return redirect('/orders/')
    
    # Расчёт рекомендуемого количества
    device_parts = DevicePart.objects.filter(part=part)
    total_per_day = 0
    for dp in device_parts:
        total_per_day += dp.quantity_per_device * dp.device.production_per_day
    recommended = int(total_per_day * part.delivery_days * 1.5)
    
    context = {
        'part': part,
        'recommended': recommended
    }
    return render(request, 'stock/order_form.html', context)

def orders_list(request):
    if not check_access(request):
        return redirect('/login')
    
    orders = Order.objects.all().order_by('-order_date')
    
    context = {
        'orders': orders,
        'is_editable': request.access_level == 'full'
    }
    return render(request, 'stock/orders_list.html', context)

def reports(request):
    if not check_access(request):
        return redirect('/login')
    
    # Статистика
    total_parts = Part.objects.count()
    low_stock = Part.objects.filter(quantity__lte=models.F('critical_minimum')).count()
    total_orders = Order.objects.filter(is_received=False).count()
    
    # Детали с низким запасом
    critical_parts = []
    for p in Part.objects.filter(is_consumable=False):
        device_parts = DevicePart.objects.filter(part=p)
        total_per_day = sum(dp.quantity_per_device * dp.device.production_per_day for dp in device_parts)
        days_left = int(p.quantity / total_per_day) if total_per_day > 0 else 999
        if days_left <= p.delivery_days:
            critical_parts.append({'part': p, 'days_left': days_left})
    
    context = {
        'total_parts': total_parts,
        'low_stock': low_stock,
        'total_orders': total_orders,
        'critical_parts': critical_parts
    }
    return render(request, 'stock/reports.html', context)

def admin_panel(request):
    if not check_access(request, 'full'):
        messages.error(request, 'Доступ только для администраторов')
        return redirect('/')
    
    # Статистика
    total_users = UserSession.objects.count()
    active_keys = AccessKey.objects.filter(is_active=True).count()
    total_logs = Log.objects.count()
    
    # Последние логи
    recent_logs = Log.objects.all().order_by('-timestamp')[:50]
    
    context = {
        'total_users': total_users,
        'active_keys': active_keys,
        'total_logs': total_logs,
        'recent_logs': recent_logs
    }
    return render(request, 'stock/admin_panel.html', context)

def create_access_key(request):
    if not check_access(request, 'full'):
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    if request.method == 'POST':
        level = request.POST.get('level')
        comment = request.POST.get('comment', '')
        
        # Генерация ключа
        import random
        import string
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        key_with_hyphens = f"{key[:4]}-{key[4:8]}-{key[8:12]}"
        
        key_hash = bcrypt.hashpw(key_with_hyphens.encode(), bcrypt.gensalt()).decode()
        
        AccessKey.objects.create(
            key_hash=key_hash,
            level=level,
            is_active=True,
            comment=comment
        )
        
        Log.objects.create(
            user=request.COOKIES.get('user_name', 'unknown'),
            action=f'Создал новый ключ доступа (уровень: {level})',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({'key': key_with_hyphens, 'level': level})
    
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)

def view_logs(request):
    if not check_access(request, 'full'):
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    logs = Log.objects.all().order_by('-timestamp')
    data = [{'user': l.user, 'action': l.action, 'timestamp': l.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'ip': l.ip_address} for l in logs]
    return JsonResponse({'logs': data})

def backup_database(request):
    if not check_access(request, 'full'):
        messages.error(request, 'Нет прав')
        return redirect('/')
    
    import subprocess
    import zipfile
    from django.conf import settings
    
    backup_dir = '/tmp/backup_msklad'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Дамп базы данных
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    
    dump_file = os.path.join(backup_dir, 'database.sql')
    os.environ['PGPASSWORD'] = db_password
    subprocess.run(['pg_dump', '-U', db_user, '-h', 'localhost', db_name, '-f', dump_file])
    
    # Создание архива
    zip_path = f'/tmp/msklad_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(dump_file, 'database.sql')
        # Добавить медиафайлы
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.join('media', file))
    
    response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="msklad_backup.zip"'
    return response

def make_admin(request, user_id):
    if not check_access(request, 'full'):
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    # Эта функция требует дополнительной модели Admins
    messages.info(request, 'Функция в разработке')
    return redirect('/admin-panel/')

def mark_order_received(request, order_id):
    """Отметить заказ как полученный"""
    if not check_access(request, 'full'):
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    order = get_object_or_404(Order, id=order_id)
    order.is_received = True
    order.save()
    
    # Добавляем количество на склад
    part = order.part
    part.quantity += order.quantity_ordered
    part.save()
    
    Log.objects.create(
        user=request.COOKIES.get('user_name', 'unknown'),
        action=f'Оприходован заказ на {part.name}: {order.quantity_ordered} шт',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({'success': True})

def device_composition(request, device_id):
    """Просмотр состава прибора (AJAX)"""
    if not check_access(request):
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    device = get_object_or_404(Device, id=device_id)
    device_parts = DevicePart.objects.filter(device=device).select_related('part')
    
    data = {
        'device_name': device.name,
        'parts': [{
            'name': dp.part.name,
            'quantity': dp.quantity_per_device
        } for dp in device_parts]
    }
    return JsonResponse(data)

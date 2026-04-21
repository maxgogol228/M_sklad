from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.core.paginator import Paginator
from .models import Part, Device, DevicePart, Order
import os
from datetime import datetime
from django.db.models import F

def index(request):
    """Главная страница"""
    return redirect('/dashboard/')

def dashboard(request):
    devices = Device.objects.all()
    parts = Part.objects.filter(is_consumable=False)
    consumables = Part.objects.filter(is_consumable=True)
    
    context = {
        'devices': devices,
        'parts': parts,
        'consumables': consumables,
    }
    return render(request, 'stock/dashboard.html', context)

def parts_list(request):
    """Список деталей"""
    parts = Part.objects.filter(is_consumable=False)
    search = request.GET.get('search', '')
    if search:
        parts = parts.filter(name__icontains=search)
    
    paginator = Paginator(parts, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'parts': page_obj,
        'search': search
    }
    return render(request, 'stock/parts_list.html', context)

def part_add(request):
    """Добавление детали"""
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
        
        messages.success(request, f'Деталь "{name}" добавлена')
        return redirect('/parts/')
    
    return render(request, 'stock/part_form.html', {'title': 'Добавить деталь'})

def part_edit(request, part_id):
    """Редактирование детали"""
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
        messages.success(request, 'Изменения сохранены')
        return redirect('/parts/')
    
    return render(request, 'stock/part_form.html', {'part': part, 'title': 'Редактировать деталь'})

def part_delete(request, part_id):
    """Удаление детали"""
    part = get_object_or_404(Part, id=part_id)
    part.delete()
    return JsonResponse({'success': True})

def devices_list(request):
    """Список приборов"""
    devices = Device.objects.all()
    return render(request, 'stock/devices_list.html', {'devices': devices})

def device_add(request):
    """Добавление прибора"""
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
        
        messages.success(request, f'Прибор "{name}" добавлен')
        return redirect('/devices/')
    
    parts = Part.objects.filter(is_consumable=False)
    return render(request, 'stock/device_form.html', {'parts': parts, 'title': 'Добавить прибор'})

def device_edit(request, device_id):
    """Редактирование прибора"""
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


def assemble_device(request, device_id):
    if request.method == 'POST':
        try:
            device = Device.objects.get(id=device_id)
            device_parts = DevicePart.objects.filter(device=device)
            
            # Проверяем, хватает ли деталей
            for dp in device_parts:
                if dp.part.quantity < dp.quantity_per_device:
                    return JsonResponse({
                        'success': False,
                        'error': f'Не хватает детали: {dp.part.name}'
                    })
            
            # Списываем детали
            for dp in device_parts:
                dp.part.quantity -= dp.quantity_per_device
                dp.part.save()
            
            return JsonResponse({'success': True})
            
        except Device.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Прибор не найден'})
    
    return JsonResponse({'success': False, 'error': 'Метод не разрешён'})

def device_composition(request, device_id):
    """Состав прибора (AJAX)"""
    device = get_object_or_404(Device, id=device_id)
    device_parts = DevicePart.objects.filter(device=device).select_related('part')
    
    data = {
        'device_name': device.name,
        'parts': [{'name': dp.part.name, 'quantity': dp.quantity_per_device} for dp in device_parts]
    }
    return JsonResponse(data)

def consumables_list(request):
    """Список расходников"""
    consumables = Part.objects.filter(is_consumable=True)
    return render(request, 'stock/consumables_list.html', {'consumables': consumables})

def create_order(request, part_id):
    """Создание заказа"""
    part = get_object_or_404(Part, id=part_id)
    
    if request.method == 'POST':
        quantity = float(request.POST.get('quantity', 0))
        Order.objects.create(part=part, quantity_ordered=quantity, is_received=False)
        messages.success(request, f'Заказ на {part.name} создан')
        return redirect('/orders/')
    
    return render(request, 'stock/order_form.html', {'part': part})

def orders_list(request):
    """Список заказов"""
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'stock/orders_list.html', {'orders': orders})

def mark_order_received(request, order_id):
    """Отметить заказ как полученный"""
    order = get_object_or_404(Order, id=order_id)
    order.is_received = True
    order.save()
    
    part = order.part
    part.quantity += order.quantity_ordered
    part.save()
    
    return JsonResponse({'success': True})

def reports(request):
    """Отчёты"""
    total_parts = Part.objects.count()
    low_stock = Part.objects.filter(quantity__lte=models.F('critical_minimum')).count()
    total_orders = Order.objects.filter(is_received=False).count()
    
    context = {
        'total_parts': total_parts,
        'low_stock': low_stock,
        'total_orders': total_orders
    }
    return render(request, 'stock/reports.html', context)

def backup_database(request):
    """Скачать бэкап базы данных"""
    import zipfile
    from django.conf import settings
    
    backup_dir = '/tmp/backup_msklad'
    os.makedirs(backup_dir, exist_ok=True)
    
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        import shutil
        shutil.copy(db_path, os.path.join(backup_dir, 'db.sqlite3'))
    
    zip_path = f'/tmp/msklad_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(os.path.join(backup_dir, 'db.sqlite3'), 'db.sqlite3')
    
    response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="msklad_backup.zip"'
    return response

import stock.models as models

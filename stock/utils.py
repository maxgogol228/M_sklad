from datetime import datetime, timedelta
from .models import Part, DevicePart

def calculate_critical_minimum(part):
    """Автоматический расчёт критического минимума"""
    device_parts = DevicePart.objects.filter(part=part)
    total_per_day = 0
    for dp in device_parts:
        total_per_day += dp.quantity_per_device * dp.device.production_per_day
    
    # Крит. минимум = потребление в день * время доставки * 1.2
    return total_per_day * part.delivery_days * 1.2

def check_low_stock():
    """Проверка низких остатков"""
    low_stock_parts = []
    for part in Part.objects.filter(is_consumable=False):
        critical = calculate_critical_minimum(part)
        if part.quantity <= critical:
            low_stock_parts.append({
                'name': part.name,
                'current': part.quantity,
                'critical': critical,
                'days_left': part.quantity / (critical / part.delivery_days) if critical > 0 else 0
            })
    return low_stock_parts
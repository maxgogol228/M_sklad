from django.contrib import admin
from .models import Part, Device, DevicePart, Order

admin.site.register(Part)
admin.site.register(Device)
admin.site.register(DevicePart)
admin.site.register(Order)

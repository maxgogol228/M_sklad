from django.contrib import admin
from .models import AccessKey, UserSession, Part, Device, DevicePart, Order, Log

admin.site.register(AccessKey)
admin.site.register(UserSession)
admin.site.register(Part)
admin.site.register(Device)
admin.site.register(DevicePart)
admin.site.register(Order)
admin.site.register(Log)
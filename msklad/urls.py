from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Автоматическое создание ключа администратора
try:
    from stock.views import ensure_admin_key
    ensure_admin_key()
except Exception as e:
    print(f"Admin key creation error: {e}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

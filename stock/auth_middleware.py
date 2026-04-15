from django.shortcuts import redirect
from django.utils.timezone import now
from datetime import timedelta
from .models import UserSession, AccessKey

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Исключения для страниц входа и статики
        if request.path.startswith('/login') or request.path.startswith('/static') or request.path.startswith('/media'):
            return self.get_response(request)
        
        # Проверка сессии по device_id (для 7-дневного окна)
        device_id = request.COOKIES.get('device_id')
        
        if device_id:
            try:
                session = UserSession.objects.get(device_id=device_id, is_active=True)
                # Проверяем, не истекли ли 7 дней
                if now() - session.last_login < timedelta(days=7):
                    # Сессия валидна
                    request.user_name = session.user_name
                    # Получаем уровень доступа из ключа
                    try:
                        key_obj = AccessKey.objects.get(key=session.access_key_hash, is_active=True)
                        request.access_level = key_obj.level
                        request.is_admin = (key_obj.level == 'admin')
                    except AccessKey.DoesNotExist:
                        request.access_level = 'observer'
                        request.is_admin = False
                    return self.get_response(request)
            except UserSession.DoesNotExist:
                pass
        
        # Если сессии нет или она истекла - перенаправляем на логин
        return redirect('/login')

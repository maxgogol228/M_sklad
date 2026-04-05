from django.shortcuts import redirect
from django.utils.timezone import now
from datetime import timedelta
from stock.models import UserSession

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/login') or request.path.startswith('/static') or request.path.startswith('/media'):
            return self.get_response(request)

        device_id = request.COOKIES.get('device_id')
        if device_id:
            try:
                session = UserSession.objects.get(device_id=device_id, is_active=True)
                if now() - session.last_login < timedelta(days=7):
                    request.user_name = session.user_name
                    request.access_level = AccessKey.objects.get(key_hash=session.access_key_hash).level
                    return self.get_response(request)
            except:
                pass

        return redirect('/login')
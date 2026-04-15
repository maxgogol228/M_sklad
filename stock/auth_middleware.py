from django.shortcuts import redirect

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/login') or request.path.startswith('/static') or request.path.startswith('/media'):
            return self.get_response(request)
        
        if not request.session.get('user_name'):
            return redirect('/login')
        
        request.user_name = request.session.get('user_name')
        request.access_level = request.session.get('access_level', 'observer')
        request.is_admin = request.session.get('is_admin', False)
        
        return self.get_response(request)

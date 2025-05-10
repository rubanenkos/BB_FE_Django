from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require authentication
        public_urls = ['/login/', '/register/', '/']
        
        # If on root URL and not authenticated, redirect to login
        if request.path == '/' and 'user' not in request.session:
            return redirect('login')
            
        # For all other URLs, check authentication
        if request.path not in public_urls and 'user' not in request.session:
            return redirect('login')
            
        response = self.get_response(request)
        return response
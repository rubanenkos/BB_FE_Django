from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import requests
import json

# Create your views here.
def index(request): 
    return render(request, 'main/index.html')

def about(request): 
    return render(request, 'main/about.html')

def users(request):
    response = requests.get(f'{settings.BACKEND_API_URL}/users')
    users = response.json()
    return render(request, 'main/users.html', {'users': users})

def donors(request):
    response = requests.get(f'{settings.BACKEND_API_URL}/donors')
    donors = response.json()
    return render(request, 'main/donors.html', {'donors': donors})

def contacts(request): 
    return render(request, 'main/contacts.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        data = {
            "name": "",
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(
                f'{settings.BACKEND_API_URL}/login',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                return redirect('home')
            else:
                return render(request, 'main/login.html', {'error': 'Invalid credentials'})
                
        except requests.exceptions.RequestException as e:
            return render(request, 'main/login.html', {'error': 'Connection error'})
            
    return render(request, 'main/login.html')

def register(request):
    if request.method == 'POST':
        # Add registration logic here
        return redirect('login')
    return render(request, 'main/register.html')
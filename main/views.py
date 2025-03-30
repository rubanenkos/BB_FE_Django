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
            # Login request
            response = requests.post(
                f'{settings.BACKEND_API_URL}/login',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                # Get user details
                user_response = requests.get(
                    f'{settings.BACKEND_API_URL}/user/email',
                    params={'email': email}
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    # Store user data in session
                    request.session['user'] = {
                        'name': user_data['name'],
                        'email': user_data['email'],
                        'role_id': user_data['role_id'],
                        'user_id': user_data['user_id']
                    }
                    return redirect('home')
                    
            return render(request, 'main/login.html', {'error': 'Invalid credentials'})
                
        except requests.exceptions.RequestException as e:
            return render(request, 'main/login.html', {'error': 'Connection error'})
            
    return render(request, 'main/login.html')

def register(request):
    if request.method == 'POST':
        # Add registration logic here
        return redirect('login')
    return render(request, 'main/register.html')

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    return redirect('login')
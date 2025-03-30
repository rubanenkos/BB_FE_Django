from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import requests
import json
from django.contrib import messages

# Create your views here.
def index(request): 
    return render(request, 'main/index.html')

def about(request): 
    return render(request, 'main/about.html')

def users(request):
    # Fetch users
    users_response = requests.get(f'{settings.BACKEND_API_URL}/users')
    users = users_response.json()
    
    # Fetch roles
    roles_response = requests.get(f'{settings.BACKEND_API_URL}/roles')
    roles = roles_response.json()
    
    print("Roles:", roles)  # Debug print to verify roles data
    return render(request, 'main/users.html', {
        'users': users,
        'roles': roles
    })

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

def add_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        role_id = request.POST.get('role_id')
        
        data = {
            "name": name,
            "email": email,
            "password": email,  # Using email as password
            "role_id": int(role_id)  # Convert to integer
        }
        
        try:
            response = requests.post(
                f'{settings.BACKEND_API_URL}/register',
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                messages.success(request, 'User created successfully')
            else:
                messages.error(request, 'Error creating user')
                
        except requests.exceptions.RequestException:
            messages.error(request, 'Connection error')
            
    return redirect('users')
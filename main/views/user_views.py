import json
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from requests.exceptions import RequestException

def users(request):
    try:
        # Fetch users
        response = requests.get(f'{settings.BACKEND_API_URL}/users')
        users = []
        if response.status_code == 200:
            users = response.json()
           
        # Fetch roles for the Add new user dropdown
        roles_response = requests.get(f'{settings.BACKEND_API_URL}/roles')
        roles = []
        if roles_response.status_code == 200:
            # Filter out roles for dropdown options
            roles = [role for role in roles_response.json() if role['role_id'] in [2, 3, 4]]

        return render(request, 'main/users.html', {
            'users': users,
            'roles': roles
        })
    except requests.exceptions.RequestException:
        messages.error(request, 'Error fetching data')
        return render(request, 'main/users.html', {
            'users': [],
            'roles': []
        })

def user_details(request):
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    return render(request, 'main/user_details.html', {
        'user': user
    })

def add_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        role_id = request.POST.get('role_id')
        
        data = {
            "name": name,
            "email": email,
            "password": email,  # Using email as password
            "role_id": int(role_id)  
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
            
            if response.status_code == 201:
                messages.success(request, 'User created successfully')
            else:
                messages.error(request, 'Error creating user')
                
        except requests.exceptions.RequestException:
            messages.error(request, 'Connection error')
            
    return redirect('users')

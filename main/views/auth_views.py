import json
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

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
                    
                    # Check if user has allowed role
                    allowed_roles = [1, 2, 4]
                    if user_data['role_id'] not in allowed_roles:
                        messages.error(request, 'Access denied. You do not have permission to log in.')
                        return render(request, 'main/login.html', {
                            'error': 'Access denied',
                            'email': email
                        })
                    
                    # Fetch roles to get role name
                    roles_response = requests.get(f'{settings.BACKEND_API_URL}/roles')
                    if roles_response.status_code == 200:
                        roles = roles_response.json()
                        role_mapping = {role['role_id']: role['name'] for role in roles}
                        role_name = role_mapping.get(user_data['role_id'], 'Unknown Role')
                    else:
                        role_name = 'Unknown Role'
                    
                    # Store user data in session with role name
                    request.session['user'] = {
                        'name': user_data['name'],
                        'email': user_data['email'],
                        'role_id': user_data['role_id'],
                        'role_name': role_name,
                        'user_id': user_data['user_id']
                    }
                    return redirect('home')
                else:
                    messages.error(request, 'Error fetching user details')
            elif response.status_code == 401:
                return render(request, 'main/login.html', {
                    'error': 'Invalid email or password',
                    'email': email
                })
            else:
                return render(request, 'main/login.html', {
                    'error': 'Login failed. Please try again.',
                    'email': email
                })
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')
            
    return render(request, 'main/login.html')

def register(request):
    if request.method == 'POST':
        return redirect('login')
    return render(request, 'main/register.html')

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    return redirect('login')

def change_password(request):
    if request.method == 'POST':
        user = request.session.get('user')
        if not user:
            return redirect('login')

        old_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return redirect('user_details')

        try:
            response = requests.post(
                f'{settings.BACKEND_API_URL}/user/change-password/{user["user_id"]}',
                headers={'Content-Type': 'application/json'},
                json={
                    'old_password': old_password,
                    'new_password': new_password
                }
            )

            if response.status_code == 200:
                messages.success(request, 'Password changed successfully')
            else:
                messages.error(request, 'Failed to change password. Please check your current password.')

        except requests.exceptions.RequestException:
            messages.error(request, 'Connection error. Please try again later.')

        return redirect('user_details')

    return redirect('user_details')
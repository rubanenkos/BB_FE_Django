import json
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from datetime import datetime

def deliveries(request):
    try:
        # Fetch requests
        response = requests.get(f'{settings.BACKEND_API_URL}/blood-requests-hospital/2')
        blood_requests = []
        if response.status_code == 200:
            blood_requests = response.json()
            for req in blood_requests:
                if req.get('request_date'):
                    req['request_date'] = datetime.strptime(req['request_date'], '%Y-%m-%d')

        # Fetch transport specialists
        users_response = requests.get(f'{settings.BACKEND_API_URL}/users')
        transport_specialists = []
        if users_response.status_code == 200:
            users = users_response.json()
            transport_specialists = [user for user in users if user['role_id'] == 3]

        return render(request, 'main/deliveries.html', {
            'requests': blood_requests,
            'transport_specialists': transport_specialists
        })
    except requests.exceptions.RequestException:
        messages.error(request, 'Error fetching data')
        return render(request, 'main/deliveries.html', {
            'requests': [],
            'transport_specialists': []
        })

def create_transport(request, request_blood_id):
    if request.method == 'POST':
        try:
            # First update the request status
            update_data = {
                "status": "Assigned"
            }
            
            status_response = requests.put(
                f'{settings.BACKEND_API_URL}/update-blood-request/{request_blood_id}',
                headers={'Content-Type': 'application/json'},
                json=update_data
            )

            if status_response.status_code != 200:
                messages.error(request, 'Error updating request status')
                return redirect('deliveries')

            # Then create the transport
            user_id = request.POST.get('transport_specialist_id')
            
            transport_data = {
                "bank_id": 2,
                "start_time": None,
                "end_time": None,
                "user_id": int(user_id),
                "request_blood_id": request_blood_id,
                "status": "not started"
            }

            transport_response = requests.post(
                f'{settings.BACKEND_API_URL}/create-blood-transport',
                headers={'Content-Type': 'application/json'},
                json=transport_data
            )

            if transport_response.status_code == 201:
                messages.success(request, 'Transport assigned successfully')
            else:
                messages.error(request, 'Error creating transport')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid form data: {str(e)}')

    return redirect('deliveries')
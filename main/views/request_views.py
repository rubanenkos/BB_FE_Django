import json
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def blood_requests(request):
    try:
        response = requests.get(f'{settings.BACKEND_API_URL}/blood-requests-hospital/2')
        if response.status_code == 200:
            blood_requests = response.json()
            for req in blood_requests:
                if req.get('request_date'):
                    req['request_date'] = datetime.strptime(req['request_date'], '%Y-%m-%d')
                
                # Fetch details for each request
                details_response = requests.get(
                    f'{settings.BACKEND_API_URL}/blood-part-requests/{req["request_blood_id"]}'
                )
                if details_response.status_code == 200:
                    req['part_details'] = details_response.json()
                else:
                    req['part_details'] = []
        else:
            blood_requests = []

        return render(request, 'main/requests.html', {
            'requests': blood_requests,
            'today': datetime.now().strftime('%Y-%m-%d')
        })
    except requests.exceptions.RequestException:
        messages.error(request, 'Error fetching data')
        return render(request, 'main/requests.html', {
            'requests': [],
            'today': datetime.now().strftime('%Y-%m-%d')
        })

def add_request(request):
    if request.method == 'POST':
        request_date = request.POST.get('request_date')
        
        try:
            response = requests.post(
                f'{settings.BACKEND_API_URL}/create-blood-request',
                headers={'Content-Type': 'application/json'},
                json={
                    'hospital_id': 2,
                    'request_date': request_date
                }
            )

            if response.status_code == 201:
                messages.success(request, 'Request created successfully')
            else:
                messages.error(request, 'Error creating request')

        except requests.exceptions.RequestException:
            messages.error(request, 'Connection error')

    return redirect('requests')

def add_request_details(request, request_blood_id):
    if request.method == 'POST':
        try:
            blood_group_id = request.POST.get('blood_group_id')
            
            if not blood_group_id:
                messages.error(request, 'Blood group is required')
                return redirect('requests')

            data = {
                "request_blood_id": request_blood_id,
                "blood_part_id": int(request.POST.get('blood_part_id')),
                "quantity": int(request.POST.get('quantity')),
                "blood_group_id": int(blood_group_id)
            }

            response = requests.post(
                f'{settings.BACKEND_API_URL}/create-blood-part-request',
                headers={'Content-Type': 'application/json'},
                json=data
            )

            if response.status_code == 201:
                messages.success(request, 'Request details added successfully')
            else:
                messages.error(request, 'Error adding request details')

        except requests.exceptions.RequestException:
            messages.error(request, 'Connection error')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid form data')

    return redirect('requests')

def search_request(request, request_blood_id):
    try:
        response = requests.get(f'{settings.BACKEND_API_URL}/find-bank/{request_blood_id}')
        search_results = None
        
        if response.status_code == 200:
            search_results = response.json()

        return render(request, 'main/partials/search_results.html', {
            'search_results': search_results,
            'request_blood_id': request_blood_id
        })
        
    except requests.exceptions.RequestException:
        messages.error(request, 'Error searching for blood bank')
        return render(request, 'main/partials/search_results.html', {
            'search_results': None,
            'request_blood_id': request_blood_id
        })
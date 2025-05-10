import json
import time
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from requests.exceptions import RequestException

def donors(request):
    response = requests.get(f'{settings.BACKEND_API_URL}/donors')
    donors = response.json()
    return render(request, 'main/donors.html', {'donors': donors})

# def donors(request):
#     try:
#         response = requests.get(f'{settings.BACKEND_API_URL}/donors')
#         if response.status_code == 200:
#             donors = response.json()
#         else:
#             donors = []
#         return render(request, 'main/donors.html', {'donors': donors})
#     except requests.exceptions.RequestException:
#         messages.error(request, 'Error fetching donors data')
#         return render(request, 'main/donors.html', {'donors': []})

def add_donor(request):
    if request.method == 'POST':
        name = request.POST.get('user_name')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')

        register_data = {
            "name": name,
            "email": email,
            "password": email,
            "role_id": 5
        }

        try:
            # Step 1: Register user
            register_response = requests.post(
                f'{settings.BACKEND_API_URL}/register',
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                data=json.dumps(register_data)
            )

            if register_response.status_code != 201:
                messages.error(request, f'Error registering user: {register_response.text}')
                return redirect('donors')

            # Step 2: Get user_id with retries
            max_retries = 5
            retry_delay = 1  # seconds
            user_id = None

            for attempt in range(max_retries):
                try:
                    time.sleep(retry_delay)  # Wait before trying
                    user_response = requests.get(
                        f'{settings.BACKEND_API_URL}/user/email',
                        params={'email': email}
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        user_id = user_data.get('user_id')
                        if user_id:
                            break
                    
                    print(f"Attempt {attempt + 1}: Waiting for user data...")
                    
                except RequestException as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    continue

            if not user_id:
                messages.error(request, 'Failed to retrieve user ID after multiple attempts')
                return redirect('donors')

            blood_group_mapping = {
                'O+': 1, 'O-': 2,
                'A+': 4, 'A-': 5,
                'B+': 6, 'B-': 7,
                'AB+': 8, 'AB-': 9
            }

            blood_group = request.POST.get('blood_group')
            rhesus = request.POST.get('rhesus_factor')
            blood_key = f"{blood_group}{'+' if rhesus == 'positive' else '-'}"
            blood_group_id = blood_group_mapping.get(blood_key)

            # Step 3: Create donor with obtained user_id
            donor_data = {
                "user_id": user_id,
                "blood_group_id": blood_group_id,
                "contact_number": request.POST.get('contact_number'),
                "sex": request.POST.get('sex'),
                "date_of_birth": date_of_birth
            }

            donor_response = requests.post(
                f'{settings.BACKEND_API_URL}/create-donor',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(donor_data)
            )

            if donor_response.status_code == 201:
                messages.success(request, 'Donor added successfully')
            else:
                messages.error(request, f'Error creating donor: {donor_response.text}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')

    return redirect('donors')
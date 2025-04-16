import time
import requests
import json
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests.exceptions import RequestException


# Create your views here.
def index(request): 
    return render(request, 'main/index.html')

def about(request): 
    return render(request, 'main/about.html')

def users(request):
    # Fetch users
    users_response = requests.get(f'{settings.BACKEND_API_URL}/users')
    users = users_response.json()
    # users = [user for user in all_users if user['role_id'] != 1]
    
    # Fetch roles
    roles_response = requests.get(f'{settings.BACKEND_API_URL}/roles')
    roles = roles_response.json()
    
    # Filter roles to only allow 2,3,4
    allowed_roles = [role for role in roles if role['role_id'] in [2, 3, 4]]
    
    return render(request, 'main/users.html', {
        'users': users,
        'roles': allowed_roles
    })

def donors(request):
    response = requests.get(f'{settings.BACKEND_API_URL}/donors')
    donors = response.json()
    return render(request, 'main/donors.html', {'donors': donors})

def deliveries(request):
    try:
        # Fetch requests
        requests_response = requests.get(f'{settings.BACKEND_API_URL}/blood-requests-hospital/2')
        blood_requests = []
        if requests_response.status_code == 200:
            blood_requests = requests_response.json()
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

def contacts(request): 
    return render(request, 'main/contacts.html')

def analytics(request):
    return render(request, 'main/analytics.html')

def supply(request):
    try:
        supplies_response = requests.get(f'{settings.BACKEND_API_URL}/supplies/2')
        if supplies_response.status_code == 200:
            supplies = supplies_response.json()
            # Convert RFC 2822 dates to datetime objects
            for supply in supplies:
                if supply.get('supply_date'):
                    supply_date = parsedate_to_datetime(supply['supply_date'])
                    supply['supply_date'] = supply_date

                # Fetch details for each supply
                details_response = requests.get(
                    f'{settings.BACKEND_API_URL}/supply-details/{supply["supply_id"]}'
                )
                if details_response.status_code == 200:
                    details = details_response.json()
                    # Convert dates in details
                    for detail in details:
                        if detail.get('creation_date'):
                            detail['creation_date'] = parsedate_to_datetime(detail['creation_date'])
                        if detail.get('expiry_date'):
                            detail['expiry_date'] = parsedate_to_datetime(detail['expiry_date'])
                    supply['details'] = details
                else:
                    supply['details'] = []    
        else:
            supplies = []

        centers_response = requests.get(f'{settings.BACKEND_API_URL}/centers')
        centers = centers_response.json() if centers_response.status_code == 200 else []
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        return render(request, 'main/supply.html', {
            'supplies': supplies,
            'centers': centers,
            'today': today
        })
    except requests.exceptions.RequestException:
        messages.error(request, 'Error fetching data')
        return render(request, 'main/supply.html', {
            'supplies': [],
            'centers': []
        })

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
            else:
                messages.error(request, 'Invalid login credentials')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')
            
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
            
            if response.status_code == 201:
                messages.success(request, 'User created successfully')
            else:
                messages.error(request, 'Error creating user')
                
        except requests.exceptions.RequestException:
            messages.error(request, 'Connection error')
            
    return redirect('users')

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

            # Continue with the rest of your existing code...
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

def add_supply(request):
    if request.method == 'POST':
        blood_donation_center_id = request.POST.get('blood_donation_center_id')
        supply_date = request.POST.get('supply_date')

        data = {
            "blood_bank_id": 2,  # Hardcoded for now
            "blood_donation_center_id": int(blood_donation_center_id),
            "supply_date": supply_date
        }

        try:
            response = requests.post(
                f'{settings.BACKEND_API_URL}/create-supply',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )

            if response.status_code == 201:
                messages.success(request, 'Supply created successfully')
            else:
                messages.error(request, f'Error creating supply: {response.text}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')

    return redirect('supply')

def add_supply_details(request, supply_id):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        rhesus_factor = request.POST.get('rhesus_factor')
        creation_date = request.POST.get('creation_date')

        # Map blood group and rhesus factor to blood_group_id
        blood_group_mapping = {
            'O+': 1, 'O-': 2,
            'A+': 4, 'A-': 5,
            'B+': 6, 'B-': 7,
            'AB+': 8, 'AB-': 9
        }

        # Combine blood group and rhesus factor
        blood_key = f"{blood_group}{'+' if rhesus_factor == 'positive' else '-'}"
        blood_group_id = blood_group_mapping.get(blood_key)

        # Calculate expiry date (2 months from creation date)
        creation_date_obj = datetime.strptime(creation_date, '%Y-%m-%d')
        expiry_date = creation_date_obj + timedelta(days=60)
        
        data = {
            "supply_id": supply_id,
            "blood_group_id": blood_group_id,
            "creation_date": creation_date,
            "expiry_date": expiry_date.strftime('%Y-%m-%d')
        }

        try:
            response = requests.post(
                f'{settings.BACKEND_API_URL}/create-supply-detail',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )

            if response.status_code == 201:
                messages.success(request, 'Supply details added successfully')
            else:
                messages.error(request, f'Error adding supply details: {response.text}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')

    return redirect('supply')

def process_supply(request, supply_id):
    if request.method == 'POST':
        try:
            response = requests.get(f'{settings.BACKEND_API_URL}/process-supply/{supply_id}')
            
            if response.status_code == 200:
                messages.success(request, 'Supply was successfully processed')
            else:
                messages.error(request, 'Error processing supply')
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')
            
    return redirect('supply')

def blood_requests(request):
    try:
        # Fetch requests
        requests_response = requests.get(f'{settings.BACKEND_API_URL}/blood-requests-hospital/2')
        blood_requests = []
        if requests_response.status_code == 200:
            blood_requests = requests_response.json()
            for req in blood_requests:
                if req.get('request_date'):
                    req['request_date'] = datetime.strptime(req['request_date'], '%Y-%m-%d')
                
                # Fetch details for each request
                details_response = requests.get(
                    f'{settings.BACKEND_API_URL}/blood-part-requests/{req["request_blood_id"]}'
                )
                if details_response.status_code == 200:
                    details = details_response.json()
                    # Add blood group mapping to each detail
                    blood_group_mapping = {
                        1: 'O+', 2: 'O-',
                        4: 'A+', 5: 'A-',
                        6: 'B+', 7: 'B-',
                        8: 'AB+', 9: 'AB-'
                    }
                    for detail in details:
                        # Debug print to check the response
                        # print(f"Detail before mapping: {detail}")
                        blood_group_id = detail.get('blood_group_id')
                        # print(f"Blood group ID: {blood_group_id}")
                        detail['blood_group'] = blood_group_mapping.get(blood_group_id, 'Unknown')
                        # print(f"Mapped blood group: {detail['blood_group']}")
                    req['part_details'] = details
                else:
                    req['part_details'] = []

        # Fetch blood parts for dropdown
        parts_response = requests.get(f'{settings.BACKEND_API_URL}/blood-parts')
        blood_parts = []
        if parts_response.status_code == 200:
            blood_parts = parts_response.json()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        return render(request, 'main/requests.html', {
            'requests': blood_requests,
            'blood_parts': blood_parts,
            'today': today
        })
    except requests.exceptions.RequestException:
        messages.error(request, 'Error fetching data')
        return render(request, 'main/requests.html', {
            'requests': [],
            'blood_parts': [],
            'today': datetime.now().strftime('%Y-%m-%d')
        })
    
def add_request(request):
    if request.method == 'POST':
        try:
            data = {
                "hospital_id": 2,  # Hardcoded for now
                "request_date": request.POST.get('request_date'),
                "status": "Pending",
            }

            response = requests.post(
                f'{settings.BACKEND_API_URL}/create-blood-request',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )

            if response.status_code == 201:
                messages.success(request, 'Request created successfully')
            else:
                messages.error(request, f'Error creating request: {response.text}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')

    return redirect('requests')

def add_request_details(request, request_blood_id):
    if request.method == 'POST':
        try:
            # Get form data directly from blood_group_id field
            blood_group_id = request.POST.get('blood_group_id')
            
            if not blood_group_id:
                messages.error(request, 'Blood group is required')
                return redirect('requests')

            data = {
                "request_blood_id": request_blood_id,
                "blood_part_id": int(request.POST.get('blood_part_id')),
                "quantity": int(request.POST.get('quantity')),
                "blood_group_id": int(blood_group_id)  # Use the blood_group_id directly
            }

            response = requests.post(
                f'{settings.BACKEND_API_URL}/create-blood-part-request',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )

            if response.status_code == 201:
                messages.success(request, 'Request details added successfully')
            else:
                messages.error(request, f'Error adding request details: {response.text}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid form data: {str(e)}')

    return redirect('requests')

def search_request(request, request_blood_id):
    try:
        # Fetch search results
        response = requests.get(f'{settings.BACKEND_API_URL}/find-bank/{request_blood_id}')
        search_results = None
        
        if response.status_code == 200:
            search_results = response.json()
            # Map blood groups in matched quantities
            blood_group_mapping = {
                1: 'O+', 2: 'O-', 4: 'A+', 5: 'A-',
                6: 'B+', 7: 'B-', 8: 'AB+', 9: 'AB-'
            }
            
            if search_results.get('matched_quantities'):
                for match in search_results['matched_quantities']:
                    bg_id = match.get('blood_group_id')
                    match['blood_group'] = blood_group_mapping.get(bg_id, 'Unknown')

            if search_results.get('missing_quantities'):
                for missing in search_results['missing_quantities']:
                    bg_id = missing.get('blood_group_id')
                    missing['blood_group'] = blood_group_mapping.get(bg_id, 'Unknown')

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
    
def approve_request(request, request_blood_id):
    if request.method == 'POST':
        try:
            # Send request to bank endpoint
            response = requests.get(
                f'{settings.BACKEND_API_URL}/send-request/{request_blood_id}/2'  # 2 is hardcoded bank_id
            )

            if response.status_code == 201:
                messages.success(request, 'Request sent to blood bank successfully')
            else:
                messages.error(request, 'Error sending request to blood bank')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')

    return redirect('requests')

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
                data=json.dumps(update_data)
            )

            if status_response.status_code != 200:
                messages.error(request, 'Error updating request status')
                return redirect('deliveries')

            # Then create the transport
            user_id = request.POST.get('transport_specialist_id')
            
            transport_data = {
                "bank_id": 2,  # Hardcoded as specified
                "start_time": None,
                "end_time": None,
                "user_id": int(user_id),
                "request_blood_id": request_blood_id,
                "status": "not started"
            }

            transport_response = requests.post(
                f'{settings.BACKEND_API_URL}/create-blood-transport',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(transport_data)
            )

            if transport_response.status_code == 201:
                messages.success(request, 'Transport assigned successfully')
            else:
                messages.error(request, 'Error creating transport')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Connection error: {str(e)}')

    return redirect('deliveries')
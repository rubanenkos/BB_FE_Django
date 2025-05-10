import json
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta

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

def add_supply(request):
    if request.method == 'POST':
        blood_donation_center_id = request.POST.get('blood_donation_center_id')
        supply_date = request.POST.get('supply_date')

        data = {
            "blood_bank_id": 2,  
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

import json
import requests
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings

def supply(request):
    try:
        # Fetch daily report
        response = requests.get(f'{settings.BACKEND_API_URL}/daily-report/2')
        if response.status_code == 200:
            supply_data = response.json()
            # Sort supplies by blood group and part
            sorted_inventory = sorted(
                supply_data.get('total_inventory', []),
                key=lambda x: (x['blood_group_name'], x['blood_part_name'])
            )
        else:
            sorted_inventory = []

        return render(request, 'main/supply.html', {
            'inventory': sorted_inventory
        })
    except requests.exceptions.RequestException:
        messages.error(request, 'Error fetching supply data')
        return render(request, 'main/supply.html', {
            'inventory': []
        })